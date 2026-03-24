from pathlib import Path

import torch
from huggingface_hub import snapshot_download
from transformers import AutoProcessor, Gemma3nForConditionalGeneration

model_id = "google/gemma-3n-e4b-it"
model_dir = Path(__file__).resolve().parent / "models" / model_id.replace("/", "--")

if not (model_dir / "config.json").exists():
    model_dir.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=model_id,
        local_dir=str(model_dir),
    )

model = Gemma3nForConditionalGeneration.from_pretrained(
    str(model_dir),
    device_map="auto",
    torch_dtype=torch.bfloat16,
    local_files_only=True,
).eval()

processor = AutoProcessor.from_pretrained(str(model_dir), local_files_only=True)

messages = [
    {
        "role": "system",
        "content": [{"type": "text", "text": "You are a helpful assistant."}],
    },
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg",
            },
            {"type": "text", "text": "Describe this image in detail."},
        ],
    },
]

inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to(model.device)

input_len = inputs["input_ids"].shape[-1]

with torch.inference_mode():
    generation = model.generate(**inputs, max_new_tokens=100, do_sample=False)
    generation = generation[0][input_len:]

decoded = processor.decode(generation, skip_special_tokens=True)
print(decoded)
