import os
from dataclasses import dataclass

COMMAND_REMINDER_DIR_ENV = "COMMAND_REMINDER_DIR"
DEFAULT_REPOSITORY_REPO = '~/.command-reminder/repository'


@dataclass
class Configuration:
    path: str

    @staticmethod
    def load_config():
        path = os.getenv(COMMAND_REMINDER_DIR_ENV)
        if not path:
            path = DEFAULT_REPOSITORY_REPO
        return Configuration(path)
