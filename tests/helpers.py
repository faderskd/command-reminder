import os
from unittest import mock

TEST_PATH = os.path.join(os.getcwd(), 'tmp')
from command_reminder.config.config import COMMAND_REMINDER_DIR_ENV, FISH_FUNCTIONS_PATH_ENV, HOME_DIR_ENV


def with_mocked_environment(cls):
    return mock.patch.dict('os.environ',
                           {COMMAND_REMINDER_DIR_ENV: TEST_PATH, FISH_FUNCTIONS_PATH_ENV: '/some/path',
                            HOME_DIR_ENV: TEST_PATH})(cls)
