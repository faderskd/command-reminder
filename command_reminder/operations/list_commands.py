import os
import typing
from dataclasses import dataclass

from command_reminder.config.config import Configuration, COMMANDS_FILE_NAME
from command_reminder.operations.base_processors import Processor, read_file_content, OperationData


@dataclass
class ListOperationDto(OperationData):
    tags: typing.List[str]
    pretty: bool


@dataclass
class FoundCommandsDto(OperationData):
    command: str
    name: str


class ListCommandsProcessor(Processor):
    def __init__(self, config: Configuration):
        self._config = config

    def process(self, data: OperationData) -> None:
        if not isinstance(data, ListOperationDto):
            return
        if not os.path.exists(self._config.main_repository_commands_file):
            self._print_colored([])

        merged_results = self._get_main_commands(data)
        external_repos_results = self._get_external_repos_results(data)
        merged_results.extend(external_repos_results)
        self._print_results(merged_results, data.pretty)

    def _get_main_commands(self, data: ListOperationDto):
        with open(self._config.main_repository_commands_file, 'r') as f:
            commands = read_file_content(f)
            return self._search_for_commands_with_tags(commands, data.tags)

    def _get_external_repos_results(self, data: ListOperationDto):
        external_repos_directory = self._config.external_repositories_directory()
        if not os.path.exists(external_repos_directory):
            return []

        results = []
        for external_file in os.listdir(external_repos_directory):
            external_file_path = os.path.join(external_repos_directory, external_file)
            if self._is_directory(external_file_path) and self._has_commands_file(external_file_path):
                with open(os.path.join(external_file_path, COMMANDS_FILE_NAME), 'r') as f:
                    commands = read_file_content(f)
                    results.extend(self._search_for_commands_with_tags(commands, data.tags))
        return results

    def _print_results(self, results: typing.List[FoundCommandsDto], pretty: bool):
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
                                       search_tags: typing.List[str]) -> typing.List[FoundCommandsDto]:
        results = []
        search_tags = set(search_tags)
        for (name, (content, tags)) in commands.items():
            tags = set(tags)
            if not search_tags or search_tags.issubset(tags):
                results.append(FoundCommandsDto(command=content, name=name))
        return results

    @staticmethod
    def _is_directory(directory: str) -> bool:
        return os.path.isdir(directory)
