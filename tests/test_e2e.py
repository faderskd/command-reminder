import os
import unittest
import shutil
from contextlib import redirect_stdout
from unittest import mock

from command_reminder.cli import parser
from command_reminder.config.config import COMMAND_REMINDER_DIR_ENV, HOME_DIR_ENV, REPOSITORIES_DIR, \
    MAIN_REPOSITORY_DIR, COMMANDS_FILE_NAME
from command_reminder.operations.processors import InvalidArgumentException

TEST_PATH = os.path.join(os.getcwd(), 'tmp')


class StdoutRedirectionContext:
    class ListIO:
        def __init__(self):
            self.output = []

        def write(self, s):
            if s in ("\n", ""):
                return
            self.output.append(s)

    def __enter__(self):
        buf = self.ListIO()
        self._ctx = redirect_stdout(buf)
        self._ctx.__enter__()
        return buf

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._ctx.__exit__(exc_type, exc_value, exc_traceback)


def assert_stdout() -> StdoutRedirectionContext:
    return StdoutRedirectionContext()


class BaseTestCase(unittest.TestCase):

    def tearDown(self) -> None:
        try:
            shutil.rmtree(TEST_PATH)
        except:
            pass

    @staticmethod
    def build_repositories_path() -> str:
        return os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV], REPOSITORIES_DIR)


@mock.patch.dict('os.environ', {COMMAND_REMINDER_DIR_ENV: TEST_PATH})
class CliInitTestCase(BaseTestCase):

    def test_should_init_repository(self):
        # when
        parser.parse_args(['init', '--repo', 'git@github.com:faderskd/command-reminder.git'])

        # then
        self.assertTrue(os.path.exists(BaseTestCase.build_repositories_path()))
        self.assertTrue(os.path.exists(os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV], ".git")))

    def test_should_init_directory_without_repository_given(self):
        # when
        parser.parse_args(['init'])

        # then
        self.assertTrue(os.path.exists(BaseTestCase.build_repositories_path()))
        self.assertFalse(os.path.exists(os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV], ".git")))

    @mock.patch.dict('os.environ', {COMMAND_REMINDER_DIR_ENV: TEST_PATH, HOME_DIR_ENV: ""})
    def test_should_throw_error_when_home_env_is_not_set(self):
        with self.assertRaisesRegex(InvalidArgumentException, '\\$HOME environment variable must be set'):
            # when
            parser.parse_args(['init'])

            # then
            self.assertFalse(os.path.exists(os.environ[COMMAND_REMINDER_DIR_ENV]))

    def test_should_throw_error_given_invalid_git_remote_url(self):
        with self.assertRaisesRegex(InvalidArgumentException, 'Invalid git repository url'):
            # when
            parser.parse_args(['init', '--repo', 'git@github.com/command-reminder.git'])

            # then
            self.assertFalse(os.path.exists(os.environ[COMMAND_REMINDER_DIR_ENV]))


@mock.patch.dict('os.environ', {COMMAND_REMINDER_DIR_ENV: TEST_PATH})
class CliRecordTestCase(BaseTestCase):
    def test_should_record_command(self):
        # given
        parser.parse_args(['init'])

        # when
        parser.parse_args(['record', '--name', 'mongo_login', '--command', 'mongo dburl/dbname --username abc --password pass'])

        # then
        self.assertTrue(os.path.exists(os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV],
                                                    REPOSITORIES_DIR, MAIN_REPOSITORY_DIR, COMMANDS_FILE_NAME)))

        # with assert_stdout() as stdout:
        #     parser.parse_args(['commands'])
        #     self.assertIn('mongo dburl/dbname --username abc --password pass', stdout.output)
