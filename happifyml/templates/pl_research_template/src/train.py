import os
from typing import List, Optional

import hydra
from omegaconf import DictConfig
from pytorch_lightning import Callback, LightningDataModule, LightningModule, Trainer, seed_everything
from pytorch_lightning.loggers import LightningLoggerBase
from transformers import AutoTokenizer

from src.utils import utils

os.environ["TOKENIZERS_PARALLELISM"] = "false"

log = utils.get_logger(__name__)


def train(config: DictConfig) -> Optional[float]:
    """Contains training pipeline.
    Instantiates all PyTorch Lightning objects from config.

    Args:
        config (DictConfig): Configuration composed by Hydra.

    Returns:
        Optional[float]: Metric score for hyperparameter optimization.
    """

    # Set seed for random number generators in pytorch, numpy and python.random
    if "seed" in config:
        seed_everything(config.seed, workers=True)

    # Init Transformers Tokenizer
    if not config.tokenizer._target_:
        log.info(f"Instantiating tokenizer {config.tokenizer.pretrained_model_name_or_path}")
        tokenizer: AutoTokenizer = AutoTokenizer.from_pretrained(config.tokenizer.pretrained_model_name_or_path)
    else:
        # initialize customized tokenizer
        log.info(f"Instantiating model <{config.tokenizer._target_}>")
        tokenizer: AutoTokenizer = hydra.utils.instantiate(config.tokenizer)

    # Init Lightning datamodule
    log.info(f"Instantiating datamodule <{config.datamodule._target_}>")
    datamodule: LightningDataModule = hydra.utils.instantiate(config.datamodule, tokenizer=tokenizer)

    # Init Lightning model
    log.info(f"Instantiating model <{config.model._target_}>")
    model: LightningModule = hydra.utils.instantiate(config.model, tokenizer=tokenizer)

    # Init Lightning callbacks
    callbacks: List[Callback] = []
    if "callbacks" in config:
        for _, cb_conf in config["callbacks"].items():
            if "_target_" in cb_conf:
                log.info(f"Instantiating callback <{cb_conf._target_}>")
                callbacks.append(hydra.utils.instantiate(cb_conf))

    # Init Lightning loggers
    logger: List[LightningLoggerBase] = []
    if "logger" in config:
        for _, lg_conf in config["logger"].items():
            if "_target_" in lg_conf:
                log.info(f"Instantiating logger <{lg_conf._target_}>")
                logger.append(hydra.utils.instantiate(lg_conf))

    # Init Lightning trainer
    log.info(f"Instantiating trainer <{config.trainer._target_}>")
    trainer: Trainer = hydra.utils.instantiate(config.trainer, callbacks=callbacks, logger=logger, _convert_="partial")

    # Load model if checkpoint provided
    if config.checkpoint:
        log.info(f"Loading model from {config.checkpoint}")
        model.load_from_checkpoint(config.checkpoint)

    # Send some parameters from config to all lightning loggers
    log.info("Logging hyperparameters!")
    utils.log_hyperparameters(
        config=config,
        model=model,
        datamodule=datamodule,
        trainer=trainer,
        callbacks=callbacks,
        logger=logger,
    )

    # Train the model
    total_batch_size = datamodule.train_batch_size * trainer.gpus * trainer.accumulate_grad_batches
    log.info("***** Running training *****")
    log.info(f"  Total train batch size (w. parallel, distributed & accumulation) = {total_batch_size}")
    trainer.fit(model=model, datamodule=datamodule)

    # Evaluate model on test set after training
    if not config.trainer.get("fast_dev_run"):
        log.info("Starting testing!")
        trainer.test()

    # Make sure everything closed properly
    log.info("Finalizing!")
    utils.finish(
        config=config,
        model=model,
        datamodule=datamodule,
        trainer=trainer,
        callbacks=callbacks,
        logger=logger,
    )

    if config.save_hf:
        save_dir = os.path.join(trainer.checkpoint_callback.dirpath, "hf_best_model")
        pl_model = model.load_from_checkpoint(trainer.checkpoint_callback.best_model_path)
        pl_model.model.save_pretrained(save_dir)
        if not config.tokenizer._target_:
            tokenizer.save_pretrained(save_dir)
        else:
            # tokenizer.save_pretrained(save_dir)
            pass

    # Print path to best checkpoint
    log.info(f"Best checkpoint path:\n{trainer.checkpoint_callback.best_model_path}")
    # Return metric score for hyperparameter optimization
    optimized_metric = config.get("optimized_metric")
    if optimized_metric:
        return trainer.callback_metrics[optimized_metric]
