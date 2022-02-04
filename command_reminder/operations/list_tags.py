from command_reminder.config.config import Configuration
from command_reminder.operations.base_processors import Processor, read_file_content, OperationData


class TagsProcessor(Processor):
    def __init__(self, config: Configuration):
        super().__init__()
        self.config = config

    def process(self, _: OperationData) -> None:
        with open(self.config.main_repository_commands_file) as f:
            commands = read_file_content(f)
            all_tags = set()
            for (name, (content, tags)) in commands.items():
                for t in tags:
                    all_tags.add(t)
        for t in all_tags:
            self._print_colored(t)
