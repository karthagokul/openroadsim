import yaml
import os

class ConfigLoader:
    _config = None

    @classmethod
    def load(cls, path="etc/config.yaml"):
        if cls._config is None:
            with open(path, 'r') as f:
                cls._config = yaml.safe_load(f)
        return cls._config

    @classmethod
    def get(cls, section, default=None):
        cfg = cls.load()
        return cfg.get(section, default or {})

