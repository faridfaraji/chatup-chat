import os
import socket
from pathlib import Path

from config_probe import probe

RESOURCES_PATH = Path(__file__).parent.parent / "deploy" / "config"
ENV = os.environ.get("ENVIRONMENT", "local")
hostname = socket.gethostname()


def load(environment):
    config_file = "common.yaml"
    env_config_file = f"{environment}/config.yaml"

    config = probe(path=str(RESOURCES_PATH), patterns=[config_file, env_config_file])
    config.database.url = f"{config.database.host}:{config.database.port}/{config.database.api_version}"
    config.database.url_api_version = f"{config.database.host}:{config.database.port}/{config.database.api_version}"
    return config


config = load(ENV)
