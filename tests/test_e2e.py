import os
import unittest
import shutil

from command_reminder.cli import parser
from command_reminder.config.config import COMMAND_REMINDER_DIR_ENV


class CliInitTestCase(unittest.TestCase):
    def setUp(self):
        os.environ[COMMAND_REMINDER_DIR_ENV] = os.path.join(os.getcwd(), 'tmp')

    def tearDown(self) -> None:
        del os.environ[COMMAND_REMINDER_DIR_ENV]

    def test_should_init_repository(self):
        # when
        parser.parse_args(['init', '--repo', 'git@github.com:faderskd/command-reminder.git'])

        # then
        self.assertTrue(os.path.exists(os.environ[COMMAND_REMINDER_DIR_ENV]))

        # cleanup
        shutil.rmtree(os.environ[COMMAND_REMINDER_DIR_ENV])
