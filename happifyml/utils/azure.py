from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
import os
import torch
from azureml.core import Workspace
from azureml.core.model import Model
from pathlib import Path


class AzureMixin:

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: str, workspace: Optional[str]=None, revision: Optional[Union[str,int]]=None, *model_args, **kwargs):
        """
        Download and initialize model from azure ml studio
        """
        if workspace and not os.path.isdir(pretrained_model_name_or_path):
            model = Model(workspace, pretrained_model_name_or_path, version=revision)
            print(f"Downloading {pretrained_model_name_or_path} from {workspace.name} model registry...")
            pretrained_model_name_or_path = model.download()
        
        return super(AzureMixin, cls).from_pretrained(pretrained_model_name_or_path, *model_args, **kwargs)


    def save_pretrained(
        self,
        save_directory: Union[str, os.PathLike],
        save_config: bool = True,
        state_dict: Optional[dict] = None,
        save_function: Callable = torch.save,
        workspace: Optional[Workspace] = None,
        push_to_azure: bool = False,
        push_to_hub: bool = False,
        **kwargs,
    ):
        if push_to_azure and not workspace:
            raise TypeError("push_to_azure requires Azure Workspace object")

        super().save_pretrained(save_directory, save_config, state_dict, save_function, push_to_hub, **kwargs)

        if push_to_azure:
            self.push_to_azure(save_directory, workspace)

    @staticmethod
    def push_to_azure(model_path, workspace, **kwargs):
        model_name = Path(model_path).name
        print(f"Pushing {model_name} to {workspace.name} ... ")
        Model.register(workspace=workspace, model_path=model_path, model_name=model_name, **kwargs)

