import json
import os


class BaseCredentials:
    token_path = os.path.expanduser("~/.happifyml/credentials/")


class AzureCredentials(BaseCredentials):
    prefix = "azure_config.json"

    @classmethod
    def save(cls, token):
        """
        Save token, creating folder as needed.
        """
        os.makedirs(os.path.dirname(cls.token_path), exist_ok=True)
        with open(os.path.join(cls.token_path, cls.prefix), "w") as f:
            json.dump(token, f)

    @classmethod
    def get(cls):
        """
        Get token or None if not existent.
        """
        try:
            with open(os.path.join(cls.token_path, cls.prefix), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            pass

    @classmethod
    def delete(cls):
        """
        Delete token. Do not fail if token does not exist.
        """
        try:
            os.remove(os.path.join(cls.token_path, cls.prefix))
        except FileNotFoundError:
            pass
