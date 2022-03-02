import json
import os


class BaseCredentials:
    credential_path = os.path.expanduser("~/.happifyml/credentials/")

    @classmethod
    def save(cls, credential):
        os.makedirs(os.path.dirname(cls.credential_path), exist_ok=True)
        with open(os.path.join(cls.credential_path), "w") as f:
            if cls.credential_path.endswith(".json"):
                json.dump(credential, f)
            else:
                f.write(credential)

    @classmethod
    def get(cls):
        try:
            with open(cls.credential_path, "r") as f:
                if cls.credential_path.endswith(".json"):
                    return json.load(f)
                else:
                    return f.read()
        except FileNotFoundError:
            pass

    @classmethod
    def delete(cls):
        try:
            os.remove(cls.credential_path)
        except FileNotFoundError:
            pass


class AzureCredentials(BaseCredentials):
    credential_path = os.path.join(BaseCredentials.credential_path, "azure_configs.json")

    @classmethod
    def get(cls, name=None):
        credential = super(AzureCredentials, cls).get()
        if name:
            credential['workspace_name'] = name
        return credential
    

class HfCredentials(BaseCredentials):
    # based on https://github.com/huggingface/huggingface_hub/blob/46843f5bb34bdbe21ea22b00e86edca81bef7e80/src/huggingface_hub/hf_api.py#L1449
    credential_path = os.path.expanduser("~/.huggingface/token")


class WandbCredentials(BaseCredentials):
    credential_path = os.path.join(BaseCredentials.credential_path, "wandb")


if __name__ == "__main__":
    cred = AzureCredentials.get()
    print(cred)
