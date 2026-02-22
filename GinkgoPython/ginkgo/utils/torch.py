import os

import torch

from ginkgo.core.config import settings


def setup_cuda_environment():
    """Configure CUDA environment variables for optimal memory management."""
    # Enable expandable segments to reduce memory fragmentation
    if "PYTORCH_CUDA_ALLOC_CONF" not in os.environ:
        print("setting CUDA environment variables...")
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"


def limit_gpu_memory(device_index: int = 0):
    """Limits the available VRAM that PyTorch can use based on the core config.

    Note: This is optional. If set to 0 or negative, PyTorch will use dynamic memory
    allocation without a hard limit. For models that fit in GPU memory, it's often
    better to skip this to allow the model to allocate what it needs.
    """
    if not torch.cuda.is_available():
        return

    limit_in_mb = settings.gpu_memory_limit_mb
    if limit_in_mb is None:
        return
    if limit_in_mb <= 0:
        raise RuntimeError(
            "No memory on GPU was allocated to PyTorch. Please adjust your configuration."
        )

    total_memory = torch.cuda.get_device_properties(device_index).total_memory
    limit_bytes = limit_in_mb * 1024 * 1024
    fraction = limit_bytes / total_memory

    fraction = min(1.0, max(0.0, fraction))

    if fraction < 0.99:
        torch.cuda.set_per_process_memory_fraction(fraction, device_index)
