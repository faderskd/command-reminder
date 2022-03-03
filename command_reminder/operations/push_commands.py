from command_reminder.exceptions import InvalidArgumentException

from command_reminder.operations.base_processors import Processor, OperationData

from command_reminder.config.config import Configuration
from command_reminder.operations.common.git import GitRepository


class PushCommandsToRepo(Processor):
    def __init__(self, configuration: Configuration, git: GitRepository):
        self._config = configuration
        self._git = git

    def process(self, operation: OperationData) -> None:
        main_dir = self._config.main_repository_dir
        if not self._git.is_git_repo(main_dir):
            raise InvalidArgumentException(f'Main directory: {main_dir} is not a git repo')
        self._git.push_changes_to_remote(main_dir)
