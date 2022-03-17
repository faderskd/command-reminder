import os

from command_reminder.config.config import Configuration, COMMANDS_FILE_NAME
from command_reminder.operations.base_processors import Processor, read_file_content, OperationData
from command_reminder.operations.common.dict_viewer import DirectoriesViewer


class TagsProcessor(Processor):
    def __init__(self, config: Configuration, dir_viewer: DirectoriesViewer):
        super().__init__()
        self._config = config
        self._dict_viewer = dir_viewer

    def process(self, _: OperationData) -> None:
        all_tags = set()
        for file_path in self._dict_viewer.list_all_repo_directories():
            if self._has_commands_file(file_path):
                commands_file = os.path.join(file_path, COMMANDS_FILE_NAME)
                with open(commands_file) as f:
                    commands = read_file_content(f)
                    for (name, (content, tags)) in commands.items():
                        for t in tags:
                            all_tags.add(t)
        for t in all_tags:
            self._print_colored(t)

    @staticmethod
    def _has_commands_file(external_dir_path: str):
        return COMMANDS_FILE_NAME in os.listdir(external_dir_path)
