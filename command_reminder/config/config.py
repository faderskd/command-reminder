import os
from dataclasses import dataclass

from command_reminder.common import InvalidArgumentException

COMMAND_REMINDER_DIR_ENV = "COMMAND_REMINDER_DIR"
HOME_DIR_ENV = "HOME"
DEFAULT_REPOSITORY_DIR = '.command-reminder'
REPOSITORIES_DIR = 'repositories'
MAIN_REPOSITORY_DIR = 'main'
COMMANDS_FILE_NAME = 'commands.json'
EXTENSIONS_REPOSITORY_DIR = 'extensions'


@dataclass
class Configuration:
    base_dir: str

    @staticmethod
    def load_config():
        return Configuration(Configuration.base_dir())

    @staticmethod
    def base_dir() -> str:
        home = os.getenv(HOME_DIR_ENV)
        Configuration._validate(home)
        path = os.getenv(COMMAND_REMINDER_DIR_ENV)
        if not path:
            path = os.path.join(home, DEFAULT_REPOSITORY_DIR)
        return path

    @property
    def repositories_dir(self) -> str:
        return os.path.join(self.base_dir, REPOSITORIES_DIR)

    @property
    def main_repository_dir(self) -> str:
        return os.path.join(self.repositories_dir, MAIN_REPOSITORY_DIR)

    @property
    def main_repository_commands_file(self) -> str:
        return os.path.join(self.main_repository_dir, COMMANDS_FILE_NAME)

    @staticmethod
    def _validate(home: str):
        if not home:
            raise InvalidArgumentException("$HOME environment variable must be set")
