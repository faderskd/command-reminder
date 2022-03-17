import json
import os
from dataclasses import dataclass

from command_reminder.config.config import Configuration
from command_reminder.operations.base_processors import Processor, read_file_content, OperationData
from command_reminder.exceptions import InvalidArgumentException


@dataclass
class RemoveCommandDto:
    command_name: str


class RemoveCommandProcessor(Processor):
    def __init__(self, config: Configuration):
        super().__init__()
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, RemoveCommandDto):
            return
        if not os.path.exists(self._config.main_repository_commands_file):
            return
        self.remove_command(data)
        self.remove_fish_function(data)

    def remove_command(self, data: RemoveCommandDto):
        with open(self._config.main_repository_commands_file, 'r+') as f:
            commands = read_file_content(f)
            if data.command_name in commands:
                del commands[data.command_name]
            else:
                raise InvalidArgumentException(f'Command {data.command_name} does not exist.')
            f.seek(0)
            json.dump(commands, f)
            f.truncate()

    def remove_fish_function(self, data: RemoveCommandDto):
        func_file = self._config.internal_fish_function_file(data.command_name)
        if os.path.exists:
            os.remove(func_file)
