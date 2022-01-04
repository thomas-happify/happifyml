# -*- coding: utf-8 -*-
r"""
Text Tokenizer
==============
    Wrapper around AutoTokenizer.
"""
import os
from typing import Any, Dict, List, Optional, Tuple

import torch
from transformers import AutoTokenizer


class Tokenizer:
    def __init__(self, pretrained_model_name_or_path, use_fast):
        """
        can't inherent AutoTokenizer, so had to wrap like this:
        https://github.com/huggingface/transformers/blob/cd56f3fe7eae4a53a9880e3f5e8f91877a78271c/src/transformers/models/auto/tokenization_auto.py#L312-L316
        """
        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_name_or_path, use_fast=use_fast
        )

    def __call__(self, **kwargs):
        return self.tokenizer(**kwargs)

    def encode(self, sequence):
        return self.tokenizer.encode(sequence)

    def decode(
        self,
        tensor: torch.Tensor,
        skip_special_tokens: bool = False,
        clean_up_tokenization_spaces: bool = True,
    ):
        return self.tokenizer.decode(tensor, skip_special_tokens, clean_up_tokenization_spaces)
