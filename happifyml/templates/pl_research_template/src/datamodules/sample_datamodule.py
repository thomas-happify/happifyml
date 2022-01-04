import os
import random
from typing import Optional, Tuple

from datasets import load_dataset, load_from_disk
from pytorch_lightning import LightningDataModule
from torch.utils.data import ConcatDataset, DataLoader, Dataset, random_split
from transformers import DataCollatorForLanguageModeling

from src.utils import utils

log = utils.get_logger(__name__)


class SampleDataModule(LightningDataModule):
    def __init__(
        self,
        **kwargs,
    ):
        """
        Pytorch Lightning datamodule warpper to pre-process, and load
        datasets during Training/Validation/Testing

        """
        super().__init__()
        raise NotImplementedError

    def prepare_data(self):
        """SINGLE device to load, preprocess & save data."""
        raise NotImplementedError

    def setup(self, stage: str):
        """
        Load preprocessed data to ALL devices for distributed training.
        DON'T put preprocess code here otherwise it will do prerocessing on EVERY single device
        """
        raise NotImplementedError

    def train_dataloader(self):
        raise NotImplementedError

    def val_dataloader(self):
        raise NotImplementedError

    def test_dataloader(self):
        raise NotImplementedError
