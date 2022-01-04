import math

import torch
import torch.nn.functional as F
import torchmetrics
from pytorch_lightning import LightningModule
from pytorch_lightning.metrics.functional import accuracy
from torch import nn
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, MSELoss
from transformers import AdamW, AutoConfig, AutoModelForMaskedLM, get_scheduler

from src.utils import utils

log = utils.get_logger(__name__)


class Model(LightningModule):
    def __init__(self, tokenizer, **kwargs):
        """
        Implement the model like you would in Pytorch
        """
        super().__init__()
        self.save_hyperparameters()
        # self.tokenizer = tokenizer

        # config = AutoConfig.from_pretrained(self.hparams.model_name_or_path)

        # if self.hparams.model_name_or_path:
        #     self.model = AutoModelForMaskedLM.from_pretrained(
        #         self.hparams.model_name_or_path,
        #         from_tf=bool(".ckpt" in self.hparams.model_name_or_path),
        #         config=config,
        #     )
        # else:
        #     log.info("Training new model from scratch")
        #     self.model = AutoModelForMaskedLM.from_config(config)

        # self.model.resize_token_embeddings(len(tokenizer))
        raise NotImplementedError

    def forward(self, x):
        # return self.model(x).logits
        raise NotImplementedError

    def training_step(self, batch, batch_idx):
        """
        training loop
        """
        # loss = self.model(**batch).loss
        # # self.log('train_loss', loss, on_step=True, prog_bar=True, logger=True)
        # return loss
        raise NotImplementedError

    def validation_step(self, batch, batch_idx):
        """
        validation loop
        """
        # loss = self.model(**batch).loss
        # perplexity = math.exp(torch.mean(loss))
        # self.log('val_loss', loss, on_epoch=True, sync_dist=True, prog_bar=True, logger=True)
        # self.log('val_ppl_loss', perplexity, on_epoch=True, sync_dist=True, prog_bar=True, logger=True)
        raise NotImplementedError

    def configure_optimizers(self):
        """ "
        specify optimizer and any grouping
        """
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in self.model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": self.hparams.weight_decay,
            },
            {
                "params": [p for n, p in self.model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        optimizer = AdamW(optimizer_grouped_parameters, self.hparams.learning_rate)

        scheduler = get_scheduler(
            name=self.hparams.lr_scheduler_type,
            optimizer=optimizer,
            num_warmup_steps=int(self.num_training_steps * self.hparams.warmup_steps_ratio),
            num_training_steps=self.num_training_steps,
        )
        scheduler = {"scheduler": scheduler, "interval": "step", "frequency": 1}

        return [optimizer], [scheduler]

    @property
    def num_training_steps(self) -> int:
        """Total training steps inferred from datamodule and devices."""
        if self.trainer.max_steps:
            return self.trainer.max_steps

        limit_batches = self.trainer.limit_train_batches
        batches = len(self.train_dataloader())
        batches = min(batches, limit_batches) if isinstance(limit_batches, int) else int(limit_batches * batches)

        num_devices = max(1, self.trainer.num_gpus, self.trainer.num_processes)
        if self.trainer.tpu_cores:
            num_devices = max(num_devices, self.trainer.tpu_cores)

        effective_accum = self.trainer.accumulate_grad_batches * num_devices
        return (batches // effective_accum) * self.trainer.max_epochs
