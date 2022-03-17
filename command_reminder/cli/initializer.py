from command_reminder.cli.parser import Operations
from command_reminder.cli.processors import CompoundProcessor
from command_reminder.config.config import Configuration
from command_reminder.config.peristent_repository_config import PersistentConfig
from command_reminder.operations.common.dict_viewer import DirectoriesViewer
from command_reminder.operations.common.git import GitRepositoryManager
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
        config = Configuration.load_config()
        persistent_repo_config = PersistentConfig(config)
        git_repository_manager = GitRepositoryManager()
        dir_viewer = DirectoriesViewer(config)
        init_processor = InitRepositoryProcessor(config, git_repository_manager, dir_viewer)
        record_processor = RecordCommandProcessor(config)
        list_processor = ListCommandsProcessor(config)
        load_processor = LoadCommandProcessor(config)
        tags_processor = TagsProcessor(config, dir_viewer)
        remove_processor = RemoveCommandProcessor(config)
        pull_processor = PullExternalRepoProcessor(config, persistent_repo_config, git_repository_manager)
        push_processor = PushCommandsToRepo(config, git_repository_manager)
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
