from command_reminder.cli.parser import Operations
from command_reminder.cli.processors import CompoundProcessor
from command_reminder.config.config import Configuration
from command_reminder.config.peristent_repository_config import PersistentConfig
from command_reminder.operations.common.git import GitRepository
from command_reminder.operations.init_repository import InitRepositoryProcessor
from command_reminder.operations.list_commands import ListCommandsProcessor
from command_reminder.operations.list_tags import TagsProcessor
from command_reminder.operations.load_command import LoadCommandProcessor
from command_reminder.operations.pull_external_repo import PullExternalRepoProcessor
from command_reminder.operations.push_commands import PushCommandsToRepo
from command_reminder.operations.record_command import RecordCommandProcessor
from command_reminder.operations.remove_command import RemoveCommandProcessor


class AppContext:
    def __init__(self):
        self.config = Configuration.load_config()
        persistent_repo_config = PersistentConfig(self.config)
        git_repository_manager = GitRepository()
        init_processor = InitRepositoryProcessor(self.config, git_repository_manager)
        record_processor = RecordCommandProcessor(self.config)
        list_processor = ListCommandsProcessor(self.config)
        load_processor = LoadCommandProcessor(self.config)
        tags_processor = TagsProcessor(self.config)
        remove_processor = RemoveCommandProcessor(self.config)
        pull_processor = PullExternalRepoProcessor(self.config, persistent_repo_config, git_repository_manager)
        push_processor = PushCommandsToRepo(self.config, git_repository_manager)
        self.compound_processor = CompoundProcessor([
            (Operations.INIT, init_processor),
            (Operations.RECORD, record_processor),
            (Operations.LIST, list_processor),
            (Operations.LOAD, load_processor),
            (Operations.TAGS, tags_processor),
            (Operations.REMOVE, remove_processor),
            (Operations.PULL, pull_processor),
            (Operations.PUSH, push_processor)
        ])
