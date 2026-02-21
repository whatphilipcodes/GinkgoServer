from huggingface_hub import snapshot_download

model_id = "google/gemma-3-4b-it"
local_dir = "GinkgoPython/weights/" + model_id.rsplit("/", 1)[-1]

snapshot_download(repo_id=model_id, local_dir=local_dir)
