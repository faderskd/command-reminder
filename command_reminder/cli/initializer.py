from command_reminder.cli.parser import Operations
from command_reminder.cli.processors import CompoundProcessor
from command_reminder.operations import processors
from command_reminder.config.config import Configuration
from command_reminder.operations.common import GitRepository


class AppContext:
    def __init__(self):
        self.config = Configuration.load_config()
        git_repository_manager = GitRepository()
        init_processor = processors.InitRepositoryProcessor(self.config, git_repository_manager)
        record_processor = processors.RecordCommandProcessor(self.config)
        list_processor = processors.ListCommandsProcessor(self.config)
        load_processor = processors.LoadCommandProcessor(self.config)
        tags_processor = processors.TagsProcessor(self.config)
        remove_processor = processors.RemoveCommandProcessor(self.config)
        pull_processor = processors.PullExternalRepoProcessor(self.config, git_repository_manager)
        self.compound_processor = CompoundProcessor([
            (Operations.INIT, init_processor),
            (Operations.RECORD, record_processor),
            (Operations.LIST, list_processor),
            (Operations.LOAD, load_processor),
            (Operations.TAGS, tags_processor),
            (Operations.REMOVE, remove_processor),
            (Operations.PULL, pull_processor)
        ])
