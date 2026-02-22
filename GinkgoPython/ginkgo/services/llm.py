import asyncio
import json
from pathlib import Path
from typing import Optional, Tuple

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Gemma3Config,
    Gemma3TextConfig,
)

from ginkgo.core.config import settings
from ginkgo.utils.logger import get_logger
from ginkgo.utils.torch import limit_gpu_memory

logger = get_logger(__name__)


class LLMService:
    """Service for running LLM inference for classification tasks."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.tokenizer = None
            cls._instance.labels = {}
            cls._instance.system_instruction = ""
        return cls._instance

    def _load_gemma_config(self, local_path: str):
        config_path = Path(local_path) / "config.json"
        if not config_path.exists():
            raise RuntimeError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            raw_config = json.load(f)

        model_type = raw_config.get("model_type", "")
        config_cls = Gemma3TextConfig if model_type == "gemma3_text" else Gemma3Config

        try:
            return config_cls.from_pretrained(local_path, local_files_only=True)
        except Exception as e:
            logger.error(f"Failed to load Gemma 3 config from {local_path}: {str(e)}")
            raise RuntimeError(
                f"Failed to load Gemma 3 config from {local_path}: {str(e)}"
            )

    def _load_model_sync(self):
        limit_gpu_memory()
        local_path = str(settings.model_path)
        logger.info(f"Loading model from: {local_path}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        logger.info(
            f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}"
        )
        logger.info(f"Quantization enabled: {settings.enable_quantization}")

        quantization_config = None
        model_kwargs = {
            "device_map": "cuda",
            "local_files_only": True,
        }

        model_kwargs["config"] = self._load_gemma_config(local_path)

        if settings.enable_quantization:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type=settings.bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=settings.bnb_4bit_use_double_quant,
            )
            model_kwargs["quantization_config"] = quantization_config
        else:
            model_kwargs["dtype"] = torch.bfloat16

        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                local_path,
                **model_kwargs,
            )
        except Exception as e:
            logger.error(f"Failed to load model from {local_path}: {str(e)}")
            raise RuntimeError(f"Failed to load model from {local_path}: {str(e)}")

        if self.model is None:
            raise RuntimeError("Model loaded but is None")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                local_path, local_files_only=True
            )
        except Exception as e:
            logger.error(f"Failed to load tokenizer from {local_path}: {str(e)}")
            raise RuntimeError(f"Failed to load tokenizer from {local_path}: {str(e)}")

        if self.tokenizer is None:
            raise RuntimeError("Tokenizer loaded but is None")

        self._load_labels()
        logger.info("Model and tokenizer loaded successfully")

    async def initialize(self):
        """Load the model weights and tokenizer asynchronously on startup."""
        if self.model is not None:
            return

        await asyncio.to_thread(self._load_model_sync)

    def _load_labels(self):
        """Load labels and prepare the system instruction."""
        labels_path = settings.data_dir / "labels.json"
        with open(labels_path, "r") as f:
            self.labels = json.load(f)

        formatted_labels = "\n".join(
            [f"- {label}: {info['detail']}" for label, info in self.labels.items()]
        )

        self.system_instruction = f"""
### ROLE
You are an expert statement classifier specializing in political science and governance metrics.

### TASK
Match the concept discussed in the user input with exactly ONE of the labels below. 
- Classify based on the topic/concept, regardless of whether the sentiment is positive or negative.
- If the input seems nonsensical/gibberish ie. not match any category, use the label: INVALID.

### CATEGORIES
{formatted_labels}

### OUTPUT FORMAT
Output ONLY the label name in plain text. Do not include quotes, prefixes, or explanations.
"""

    def infer_gsod(self, input_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Classify the input text and return the trait and attribute_class.
        Returns:
            Tuple[Optional[str], Optional[str]]: (trait, attribute_class)
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError(
                "LLMService is not initialized. Call initialize() first."
            )

        prompt_text = (
            f"<bos><start_of_turn>developer\n{self.system_instruction.strip()}<end_of_turn>\n"
            f"<start_of_turn>user\nUser Input: {input_text}\n\nClassification:<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )

        inputs_tokens = self.tokenizer(
            prompt_text, return_tensors="pt", add_special_tokens=False
        ).to(self.model.device)

        input_length = inputs_tokens.input_ids.shape[1]

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs_tokens,
                max_new_tokens=10,
                do_sample=True,  # True
                # top_p=None,
                # top_k=None,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated_tokens = outputs[0][input_length:]

        if generated_tokens is None or generated_tokens.numel() == 0:
            logger.warning(f"No tokens generated for input: {input_text}")
            return None, None

        decoded = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        if isinstance(decoded, list):
            prediction = decoded[0].strip() if decoded else ""
        else:
            prediction = decoded.strip() if decoded else ""

        trait = prediction
        logger.debug(
            f"LLM Response - Input: {input_text[:100]}... | Prediction: {trait}"
        )

        if trait in self.labels:
            attribute_class = self.labels[trait].get("attribute")
            logger.info(
                f"Classification successful - Trait: {trait}, Attribute: {attribute_class}"
            )
            return trait, attribute_class
        elif trait == "INVALID":
            logger.info(f"Input classified as INVALID: {input_text[:100]}...")
            return trait, None

        logger.warning(
            f"Prediction '{trait}' not found in labels for input: {input_text[:100]}..."
        )
        return None, None


llm_service = LLMService()
