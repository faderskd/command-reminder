import os
import shutil
from unittest import mock

from command_reminder.operations.common.git import GitRepository

TEST_PATH = os.path.join(os.getcwd())
TEST_TMP_DIR_PATH = os.path.join(os.getcwd(), 'tmp')
from command_reminder.config.config import COMMAND_REMINDER_DIR_ENV, FISH_FUNCTIONS_PATH_ENV, HOME_DIR_ENV, \
    COMMANDS_FILE_NAME, FISH_FUNCTIONS_DIR_NAME


def with_mocked_environment(cls):
    GitRepository.pull_changes_from_remote = pull_changes_mock
    return mock.patch.dict('os.environ',
                           {COMMAND_REMINDER_DIR_ENV: TEST_TMP_DIR_PATH, FISH_FUNCTIONS_PATH_ENV: '/some/path',
                            HOME_DIR_ENV: TEST_TMP_DIR_PATH})(cls)


def pull_changes_mock(_, directory: str):
    create_fake_repo(directory)


def push_changes_mock(_, _directory: str):
    pass


def create_fake_repo(directory: str):
    create_fake_commands_file(directory)
    create_fake_fish_dir(directory)


def create_fake_commands_file(directory: str):
    target_commands_file = os.path.join(directory, COMMANDS_FILE_NAME)
    fake_commands_file = os.path.join(TEST_PATH, 'files', 'fake_commands.json')
    shutil.copy(fake_commands_file, target_commands_file)


def create_fake_fish_dir(directory: str):
    target_fish_dir = os.path.join(directory, FISH_FUNCTIONS_DIR_NAME, 'external_command.fish')
    os.makedirs(target_fish_dir)
    fake_fish_file = os.path.join(TEST_PATH, 'files', 'fake_fish_file.fish')
    shutil.copy(fake_fish_file, target_fish_dir)
