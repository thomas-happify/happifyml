from azureml.core import Workspace
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.conda_dependencies import CondaDependencies

cred = {"subscription_id": "e69e05ad-82e9-45c0-a0a9-f2dfa5a1047e", "resource_group": "rg-hh-cognitive-sandbox-001", "workspace_name": "test-training"}
# cli_auth = AzureCliAuthentication()
ws = Workspace(**cred)

run = ws.get_run("test_gpt_gpu_1644255889_59a40124")
details = run.get_details()


model = run.register_model(model_name="test", model_path="logs/runs/2022-02-07/17-46-34-pnn/checkpoints/hf_best_model/")