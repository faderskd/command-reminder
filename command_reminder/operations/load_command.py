import re
import typing
from dataclasses import dataclass

from command_reminder import common

from command_reminder.config.config import Configuration
from command_reminder.operations.base_processors import Processor, OperationData


@dataclass
class LoadCommandsListDto(OperationData):
    commands: typing.List[str]


class LoadCommandProcessor(Processor):
    COMMAND_LINE_REGEX = "[\\w+-]+: (.+)"

    def __init__(self, config: Configuration):
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, LoadCommandsListDto):
            return
        self._populate_fish_history(data.commands)

    def _populate_fish_history(self, commands: typing.List[str]):
        with open(self._config.fish_history_file, 'a') as f:
            for c in self._preprocess(commands):
                f.writelines([f'- cmd: {c}\n',
                              f'  when: {common.get_timestamp()}\n'])

    def _preprocess(self, commands: typing.List[str]) -> typing.Iterable[str]:
        filtered_commands = filter(lambda s: s.strip() and not s.strip().isspace(), commands)
        parsed_commands = list(map(lambda s: s.strip(), filtered_commands))

        for fc in parsed_commands:
            if match := re.match(self.COMMAND_LINE_REGEX, fc):
                yield match.group(1)
