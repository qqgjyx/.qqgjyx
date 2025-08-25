"""General helper utilities for environment and reproducibility."""

import platform
import sys
from typing import Optional


def print_environment_info() -> None:
    """Print information about the environment (imports on demand)."""
    # Lazy imports to avoid heavy deps at import time
    import numpy as np  # type: ignore
    import torch  # type: ignore

    print("\n=== Environment Information ===")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"PyTorch version: {getattr(torch, '__version__', 'N/A')}")
    print(f"NumPy version: {getattr(np, '__version__', 'N/A')}")
    print(f"Platform: {platform.platform()}")
    print("============================\n")


def get_device_info() -> "object":
    """Get information about available computing devices.

    Returns
    -------
    torch.device
        The device that will be used for computations (either 'cuda' or 'cpu')
    """
    import torch  # type: ignore

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("\n=== Device Information ===")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if device.type == "cuda":
        print(f"CUDA version: {torch.version.cuda}")
        print(f"CUDA device count: {torch.cuda.device_count()}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
        print(f"GPU: {torch.cuda.get_device_name()}")
    print(f"Using device: {device}")
    print("========================\n")
    return device


def set_all_seeds(seed: int = 42) -> int:
    """Set all seeds for reproducibility."""
    import numpy as np  # type: ignore
    import pytorch_lightning as pl  # type: ignore
    import torch  # type: ignore

    print("\n=== Setting Random Seeds ===")
    print(f"Seed value: {seed}")
    print("Setting torch CPU seed...")
    torch.manual_seed(seed)
    print("Setting torch CUDA seed...")
    torch.cuda.manual_seed_all(seed)
    print("Setting numpy seed...")
    np.random.seed(seed)
    print("Configuring CUDNN...")
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    print("Configuring PL...")
    pl.seed_everything(seed, workers=True)
    print("========================\n")
    return seed


__all__ = [
    "print_environment_info",
    "get_device_info",
    "set_all_seeds",
]


