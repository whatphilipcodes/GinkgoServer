import json
from pathlib import Path

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


class InspectorService:
    """Service for hosting the shared inspector model/tokenizer and providing
    inference helpers.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InspectorService, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.tokenizer = None
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

        if not torch.cuda.is_available():
            error_msg = (
                "CUDA is not available. This application requires a CUDA-enabled GPU to run. "
                "Please ensure you have:\n"
                "  1. A compatible NVIDIA GPU installed\n"
                "  2. NVIDIA CUDA Toolkit installed\n"
                "  3. Compatible NVIDIA drivers installed\n"
                "The application cannot proceed without GPU support."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

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
        logger.info("Model and tokenizer loaded successfully")

    async def initialize(self):
        if self.model is not None:
            return
        self._load_model_sync()

    def generate(
        self,
        prompt_text: str,
        max_new_tokens: int = 128,
        do_sample: bool = True,
    ) -> str:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError(
                "InspectorService is not initialized. Call initialize() first."
            )

        inputs_tokens = self.tokenizer(
            prompt_text, return_tensors="pt", add_special_tokens=False
        ).to(self.model.device)
        input_length = inputs_tokens.input_ids.shape[1]

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs_tokens,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated = outputs[0][input_length:]
        if generated is None or generated.numel() == 0:
            return ""
        decoded = self.tokenizer.decode(generated, skip_special_tokens=True)
        return decoded[0].strip() if isinstance(decoded, list) else decoded.strip()


inspector_service = InspectorService()
