import torch


def set_gpu_memory_limit(device_index, limit_in_mb):
    total_memory = torch.cuda.get_device_properties(device_index).total_memory
    limit_bytes = limit_in_mb * 1024 * 1024
    fraction = limit_bytes / total_memory

    torch.cuda.set_per_process_memory_fraction(fraction, device_index)


set_gpu_memory_limit(0, 4096)
