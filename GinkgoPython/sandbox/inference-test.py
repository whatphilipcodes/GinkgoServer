import json
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

local_path = os.path.abspath("GinkgoPython/weights/gemma-3-4b-it")

print(f"Loading model from: {local_path}\n")
print(f"CUDA available: {torch.cuda.is_available()}")
print(
    f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}\n"
)

try:
    model = AutoModelForCausalLM.from_pretrained(
        local_path,
        device_map="cuda",
        torch_dtype=torch.bfloat16,
        local_files_only=True,
    )
except Exception as e:
    raise RuntimeError(f"Failed to load model from {local_path}: {str(e)}")

if model is None:
    raise RuntimeError("Model loaded but is None")

try:
    tokenizer = AutoTokenizer.from_pretrained(local_path, local_files_only=True)
except Exception as e:
    raise RuntimeError(f"Failed to load tokenizer from {local_path}: {str(e)}")

if tokenizer is None:
    raise RuntimeError("Tokenizer loaded but is None")

labels_path = os.path.abspath("GinkgoPython/ginkgo/data/labels.json")
inputs_path = os.path.abspath("GinkgoPython/sandbox/eval/inputs.json")

with open(labels_path, "r") as f:
    labels = json.load(f)

with open(inputs_path, "r") as f:
    inputs_data = json.load(f)

formatted_labels = "\n".join(
    [f"- {label}: {info['detail']}" for label, info in labels.items()]
)

system_instruction = f"""
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

print("System instructions prepared.")
print("-" * 80)
print("\nRunning classification test on data:\n")
print("=" * 80)

english_inputs = inputs_data.get("en", [])
correct = 0
total = 0

for i, item in enumerate(english_inputs[:10]):
    text = item["text"]
    ground_truth = item["label"]

    prompt_text = (
        f"<bos><start_of_turn>developer\n{system_instruction.strip()}<end_of_turn>\n"
        f"<start_of_turn>user\nUser Input: {text}\n\nClassification:<end_of_turn>\n"
        f"<start_of_turn>model\n"
    )

    inputs_tokens = tokenizer(
        prompt_text, return_tensors="pt", add_special_tokens=False
    ).to(model.device)

    input_length = inputs_tokens.input_ids.shape[1]

    outputs = model.generate(
        **inputs_tokens,
        max_new_tokens=10,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )

    generated_tokens = outputs[0][input_length:]

    if generated_tokens is None or generated_tokens.numel() == 0:
        raise RuntimeError("Model did not generate valid tokens")

    decoded = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    if isinstance(decoded, list):
        prediction = decoded[0].strip() if decoded else ""
    else:
        prediction = decoded.strip() if decoded else ""

    is_correct = prediction == ground_truth
    if is_correct:
        correct += 1
    total += 1

    status = "✓" if is_correct else "✗"
    print(f"\n{status} Sample {i + 1}:")
    print(f"Text: {text}")
    print(f"Ground Truth: {ground_truth}")
    print(f"Prediction: {prediction}")
    print("-" * 80)

print(f"\nAccuracy: {correct}/{total} ({100 * correct / total:.1f}%)")
