# GinkgoServer

> This is the server component for the Colab Project responsible for running the frontend alongside the ML pipeline

## Setup

### REQUIREMENTS
- Windows 11 with a dedicated CUDA capable GPU (`>8GB VRAM`)
- Have [CUDA 13.0](https://developer.nvidia.com/cuda-13-0-0-download-archive) installed
```sh
nvcc --version
```
- Have `uv` installed
```sh
scoop install main/uv
```
- Have an [hf account](https://huggingface.co/) with access to the [Gemma 3](https://huggingface.co/google/gemma-3-4b-it) models
- Optional: For best DX, make sure you have the workspace recommendations installed and Pylance disabled

### INSTALLATION
1. Authenticate with an access token (`uv sync` will run automatically and install the python environment)
```sh
cd GinkgoPython && uv run hf auth login
```
2. Run [`download-gemma.py`](./GinkgoPython/sandbox/download-gemma.py), this will download the model weights and take a while
```sh
uv run sandbox/download-gemma.py
```

### LAUNCH
```sh
uv run main.py
```
