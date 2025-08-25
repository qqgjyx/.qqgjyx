"""
Drafted by Juntang Wang at Mar 5th for the GASNN project

This file contains utility functions for the project.
"""

from typing import Tuple
import platform
import sys

import matplotlib.pyplot as plt
import numpy as np
import pytorch_lightning as pl
import scienceplots  # noqa: F401  # imported to register 'science' style
import torch
from torch.utils.data import Dataset, random_split


def print_environment_info() -> None:
    """Print information about the environment."""
    print("\n=== Environment Information ===")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"NumPy version: {np.__version__}")
    print(f"Platform: {platform.platform()}")
    print("============================\n")


def get_device_info() -> torch.device:
    """Get information about available computing devices.

    Returns
    -------
    torch.device
        The device that will be used for computations (either 'cuda' or 'cpu')
    """
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


def set_plt_style() -> None:
    """Set the style for matplotlib."""
    plt.style.use("science")
    plt.rcParams.update(
        {
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.family": "sans-serif",
            "figure.dpi": 600,
            "savefig.dpi": 600,
            "figure.figsize": (10, 7),
            "font.size": 13,
            "axes.labelsize": 17,
            "axes.titlesize": 17,
            "xtick.labelsize": 13,
            "ytick.labelsize": 13,
            "legend.fontsize": 13,
            # "text.usetex": True,
        }
    )


def train_val_split(train_set: Dataset, val_ratio: float = 0.2, seed: int = 42) -> Tuple[Dataset, Dataset]:
    """
    Split the dataset into training and validation sets.

    Parameters
    ----------
    train_set : Dataset
        The dataset to be split.
    val_ratio : float, optional
        The ratio of the dataset to be used for validation (default is 0.2).
    seed : int, optional
        The seed for random number generation (default is 42).

    Returns
    -------
    Tuple[Dataset, Dataset]
        The training and validation datasets.
    """
    train_set_size = int(len(train_set) * (1 - val_ratio))
    val_set_size = len(train_set) - train_set_size
    generator = torch.Generator().manual_seed(seed)
    train_subset, val_subset = random_split(
        train_set, [train_set_size, val_set_size], generator=generator
    )
    return train_subset, val_subset


__all__ = [
    "print_environment_info",
    "get_device_info",
    "set_all_seeds",
    "set_plt_style",
    "train_val_split",
]


