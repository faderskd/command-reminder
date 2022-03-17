import json
import os
import typing
from dataclasses import dataclass

from command_reminder.config.config import Configuration
from command_reminder.operations.base_processors import Processor, read_file_content, OperationData


@dataclass
class RecordCommandOperationDto(OperationData):
    command: str
    name: str
    tags: typing.List[str]


class RecordCommandProcessor(Processor):
    ECHO_COLOR = 'blue'

    def __init__(self, config: Configuration):
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, RecordCommandOperationDto):
            return
        self._append_command(data)
        self._create_fish_function(data)

    def _append_command(self, data: RecordCommandOperationDto) -> None:
        flags = 'w+'
        if os.path.exists(self._config.main_repository_commands_file):
            flags = 'r+'
        with open(self._config.main_repository_commands_file, flags) as f:
            commands = read_file_content(f)
            f.seek(0)
            commands[data.name] = (data.command, self._preprocess_tags(data.tags))
            json.dump(commands, f)
            f.truncate()

    def _create_fish_function(self, data: RecordCommandOperationDto) -> None:
        fish_func_file = self._config.internal_fish_function_file(data.name)
        if os.path.exists(fish_func_file):
            return
        with open(fish_func_file, 'w+') as f:
            f.write(f'''
function {data.name}
    set color {self.ECHO_COLOR}; echo '{data.command}'
end''')

    @staticmethod
    def _preprocess_tags(tags: typing.List[str]) -> typing.List[str]:
        stripped = [t.strip() for t in tags]
        return [t for t in stripped if t]

