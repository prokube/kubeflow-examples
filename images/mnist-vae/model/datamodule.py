from typing import Optional
import pytorch_lightning as pl
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST
from torchvision.transforms import transforms


class MNISTDataModule(pl.LightningDataModule):
    """
    PyTorch Lightning Data Module for the MNIST dataset.

    This module handles the loading and transforming of MNIST data for use in
    training and validation.

    Attributes:
        data_path (str): Path to the directory where the MNIST data will be
        stored.
        num_workers (int): Number of subprocesses to use for data loading.
        batch_size (int): How many samples per batch to load.
    """

    def __init__(
        self, data_path: str = "./data", num_workers: int = 4, batch_size: int = 32
    ):
        """
        Initializes the MNISTDataModule.

        Args:
            data_path (str): Path to the directory where the MNIST data is
                stored.
            num_workers (int): Number of subprocesses to use for data loading.
            batch_size (int): How many samples per batch to load.
        """
        super().__init__()
        self.data_path = data_path
        self.num_workers = num_workers
        self.batch_size = batch_size
        self.train_dataset = None
        self.val_dataset = None

    def setup(self, stage: Optional[str] = None) -> None:
        """
        Prepares the MNIST datasets for training and validation.

        Args:
            stage (Optional[str]): Stage - either 'fit' or 'test'. If None,
                setup will prepare all datasets.
        """
        # Define the transform to apply to each data point
        transform = transforms.Compose([transforms.ToTensor()])

        # Download and prepare the MNIST datasets
        self.train_dataset = MNIST(
            self.data_path, train=True, download=True, transform=transform
        )
        self.val_dataset = MNIST(
            self.data_path, train=False, download=True, transform=transform
        )

    def train_dataloader(self) -> DataLoader:
        """
        Returns the DataLoader for training.

        Returns:
            DataLoader: The DataLoader for the MNIST training dataset.
        """
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
        )

    def val_dataloader(self) -> DataLoader:
        """
        Returns the DataLoader for validation.

        Returns:
            DataLoader: The DataLoader for the MNIST validation dataset.
        """
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
        )
