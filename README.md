<div align="center">

# Happify ML 

<h3 align="center">
    <p>Happify AI team MLOps Solution for Centralized, Flexible and Reproducible Modeling</p>
</h3>


</div>

## 🐳 Installation
```
pip install https://github.com/thomas-happify/happifyml.git
```

## 🚀 Quickstart

### Command Line Interface

1. Submit training to Azure compute.
```bash
hml azure <your-local-training-arguments>

# hml azure python run.py --nodes=8 --gpus=8
# hml azure bash run.sh
```

2. Register model from AML experiment.
```bash
hml azure --register <run-id> --model-name <custom-model-name> --model-path <model-remote-path-on-azure>
```

3. Switch to another Azure ML workspace.
```bash
hml azure --relogin
```

4. [TODO] Initialize research template
```bash
hml azure <project-name>
```

5. [TODO] Model deployment
```bash
hml deploy <configuration-file>
```

### Python SDK
1. Huggingface Integrations
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from happifyml import AzureMixin, AzureML

# mixin azure integrations
class AutoModelForSequenceClassification(AzureMixin, AutoModelForSequenceClassification):
    pass

class AutoTokenizer(AzureMixin, AutoTokenizer):
    pass


aml = AzureML()

tokenizer = AutoTokenizer.from_pretrained(<remote path to you azure model>, workspace=aml.workspace)
model = AutoModelForSequenceClassification.from_pretrained(<remote path to you azure model>, workspace=aml.workspace)

# you then can push to the model to registry in 2 ways:
# 1. 
model.save_pretrained(<local-save-path>, push_to_azure=True)
model.save_pretrained(<local-save-path>, push_to_azure=True, push_to_hub=True) # you can push to 2 places as well
# 2.
aml.push(<save-path>)

```


## 🧪 Tests (coming soon)

## 🧑‍💻 Packages (coming soon)