import os
import typing
from dataclasses import dataclass

from command_reminder.config.config import Configuration, COMMANDS_FILE_NAME
from command_reminder.operations.base_processors import Processor, read_file_content, OperationData
from command_reminder.operations.common.dict_viewer import DirectoriesViewer


@dataclass
class ListOperationDto(OperationData):
    tags: typing.List[str]
    pretty: bool


@dataclass
class FoundCommandDto(OperationData):
    command: str
    name: str


class ListCommandsProcessor(Processor):
    def __init__(self, config: Configuration):
        self._config = config
        self._dict_viewer = DirectoriesViewer(config)

    def process(self, data: OperationData) -> None:
        if not isinstance(data, ListOperationDto):
            return

        results = self._get_commands_from_repos(data)
        self._print_results(results, data.pretty)

    def _get_commands_from_repos(self, data: ListOperationDto) -> typing.List[FoundCommandDto]:
        results = []
        for dir_path in self._dict_viewer.list_all_repo_directories():
            if self._has_commands_file(dir_path):
                with open(os.path.join(dir_path, COMMANDS_FILE_NAME), 'r') as f:
                    commands = read_file_content(f)
                    results.extend(self._search_for_commands_with_tags(commands, data.tags))
        return results

    def _print_results(self, results: typing.List[FoundCommandDto], pretty: bool):
        for r in results:
            if pretty:
                self._print_colored(f"{r.name}: {r.command}")
            else:
                print(f"{r.name}: {r.command}")

    @staticmethod
    def _has_commands_file(external_dir_path: str):
        return COMMANDS_FILE_NAME in os.listdir(external_dir_path)

    @staticmethod
    def _search_for_commands_with_tags(commands: typing.Dict[str, typing.List[typing.List[str]]],
                                       search_tags: typing.List[str]) -> typing.List[FoundCommandDto]:
        results = []
        search_tags = set(search_tags)
        for (name, (content, tags)) in commands.items():
            tags = set(tags)
            if not search_tags or search_tags.issubset(tags):
                results.append(FoundCommandDto(command=content, name=name))
        return results
