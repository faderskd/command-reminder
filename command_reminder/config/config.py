import os
from dataclasses import dataclass

from command_reminder.common import InvalidArgumentException

COMMAND_REMINDER_DIR_ENV = "COMMAND_REMINDER_DIR"
FISH_FUNCTIONS_PATH_ENV = 'fish_function_path'
HOME_DIR_ENV = "HOME"

DEFAULT_REPOSITORY_DIR = '.command-reminder'
REPOSITORIES_DIR_NAME = 'repositories'
MAIN_REPOSITORY_DIR_NAME = 'main'
COMMANDS_FILE_NAME = 'commands.json'
EXTENSIONS_REPOSITORY_DIR_NAME = 'extensions'
FISH_FUNCTIONS_DIR_NAME = 'fish'
FISH_HISTORY_DIR = '.local/share/fish'
FISH_HISTORY_FILE_NAME = 'fish_history'
HISTORY_LOAD_FILE_NAME = 'h.fish'


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
        return os.path.join(self.base_dir, REPOSITORIES_DIR_NAME)

    @property
    def main_repository_dir(self) -> str:
        return os.path.join(self.repositories_dir, MAIN_REPOSITORY_DIR_NAME)

    @property
    def main_repository_commands_file(self) -> str:
        return os.path.join(self.main_repository_dir, COMMANDS_FILE_NAME)

    @property
    def main_repository_fish_functions(self) -> str:
        return os.path.join(self.main_repository_dir, FISH_FUNCTIONS_DIR_NAME)

    @property
    def fish_history_file(self) -> str:
        home = os.getenv(HOME_DIR_ENV)
        return os.path.join(home, FISH_HISTORY_DIR, FISH_HISTORY_FILE_NAME)

    @staticmethod
    def _validate(home: str):
        if not home:
            raise InvalidArgumentException("$HOME environment variable must be set")
