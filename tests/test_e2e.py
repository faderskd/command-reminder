import os
import unittest
import shutil
from contextlib import redirect_stdout
from typing import List
from unittest import mock

from command_reminder.common import InvalidArgumentException

from command_reminder.cli import parser
from command_reminder.config.config import COMMAND_REMINDER_DIR_ENV, HOME_DIR_ENV, REPOSITORIES_DIR_NAME, \
    MAIN_REPOSITORY_DIR_NAME, COMMANDS_FILE_NAME, FISH_FUNCTIONS_DIR_NAME, FISH_FUNCTIONS_PATH_ENV, FISH_HISTORY_DIR, \
    FISH_HISTORY_FILE_NAME
from tests.helpers import with_mocked_environment, TEST_PATH


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
    def setUp(self) -> None:
        history_dir = os.path.join(TEST_PATH, FISH_HISTORY_DIR)
        self.history_file = os.path.join(history_dir, FISH_HISTORY_FILE_NAME)
        os.makedirs(history_dir)
        with open(self.history_file, 'w') as f:
            f.write(f'''
- cmd brew install fish
  when 1639436632
''')

    def tearDown(self) -> None:
        try:
            shutil.rmtree(TEST_PATH)
        except:
            pass

    def assertOutputContains(self, stdout: List[str], expected: str):
        self.assertTrue(any(expected in s for s in stdout))


@with_mocked_environment
class CliInitTestCase(BaseTestCase):

    def test_should_init_empty_github_repository(self):
        # when
        parser.parse_args(['init', '--repo', 'git@github.com:faderskd/command-reminder.git'])

        # then
        self.assertTrue(os.path.exists(f'/{TEST_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{FISH_FUNCTIONS_DIR_NAME}'))
        self.assertTrue(os.path.exists(os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV], ".git")))

    def test_should_init_directory_without_github_repository_given(self):
        # when
        parser.parse_args(['init'])

        # then
        self.assertTrue(os.path.exists(f'/{TEST_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{FISH_FUNCTIONS_DIR_NAME}'))
        self.assertFalse(os.path.exists(os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV], ".git")))

    def test_should_return_init_script(self):
        # when
        with assert_stdout() as stdout:
            parser.parse_args(['init'])
            self.assertOutputContains(stdout.output,
                                      f'set -gx {FISH_FUNCTIONS_PATH_ENV} ${FISH_FUNCTIONS_PATH_ENV} {TEST_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{FISH_FUNCTIONS_DIR_NAME}')

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


@with_mocked_environment
class CliRecordTestCase(BaseTestCase):
    def test_should_record_command(self):
        # given
        parser.parse_args(['init'])

        # when
        parser.parse_args(
            ['record', '--name', 'mongo_login', '--command', 'mongo dburl/dbname --username abc --password pass'])

        # then
        self.assertTrue(os.path.exists(os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV],
                                                    REPOSITORIES_DIR_NAME, MAIN_REPOSITORY_DIR_NAME, COMMANDS_FILE_NAME)))

        with assert_stdout() as stdout:
            parser.parse_args(['list'])
            self.assertOutputContains(stdout.output, 'mongo_login: mongo dburl/dbname --username abc --password pass')

    def test_should_create_fish_function_joined_by_underscores(self):
        # given
        parser.parse_args(['init'])

        # when
        parser.parse_args(
            ['record', '--name', 'mongo login', '--command', 'mongo dburl/dbname --username abc --password pass'])

        # then
        function_file = os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV], REPOSITORIES_DIR_NAME, MAIN_REPOSITORY_DIR_NAME,
                                     FISH_FUNCTIONS_DIR_NAME, 'mongo_login.fish')
        self.assertTrue(os.path.exists(function_file))

        # and
        with open(function_file, 'r') as f:
            content = ''.join([line for line in f.readlines()])
            self.assertEqual(content, '''
            function mongo_login
                set color blue; echo 'mongo dburl/dbname --username abc --password pass'
            end
            ''')


@with_mocked_environment
class CliListTestCase(BaseTestCase):
    def test_should_filter_commands_by_tags(self):
        # given
        parser.parse_args(['init'])

        parser.parse_args(['record', '--name', 'mongo', '--command', 'mongo', '--tags', '#onduty #mongo'])
        parser.parse_args(['record', '--name', 'cassandra', '--command', 'cassandra', '--tags', '#onduty #cassandra'])

        # when
        with assert_stdout() as stdout:
            parser.parse_args(['list', '--tags', '#onduty'])
            self.assertEqual(len(stdout.output), 2)
            self.assertOutputContains(stdout.output, 'mongo: mongo')
            self.assertOutputContains(stdout.output, 'cassandra: cassandra')

        # when
        with assert_stdout() as stdout:
            parser.parse_args(['list', '--tags', '#mongo'])
            self.assertEqual(len(stdout.output), 1)
            self.assertOutputContains(stdout.output, 'mongo: mongo')

    def test_allow_use_tags_with_comma(self):
        # given
        parser.parse_args(['init'])

        parser.parse_args(['record', '--name', 'mongo', '--command', 'mongo', '--tags', '#onduty,#mongo'])

        with assert_stdout() as stdout:
            # when
            parser.parse_args(['list', '--tags', '#onduty'])

            # then
            self.assertEqual(len(stdout.output), 1)
            self.assertOutputContains(stdout.output, 'mongo: mongo')

        with assert_stdout() as stdout:
            # when
            parser.parse_args(['list', '--tags', '#onduty,        #mongo'])

            # then
            self.assertEqual(len(stdout.output), 1)
            self.assertOutputContains(stdout.output, 'mongo: mongo')

    def test_should_list_all_commands_when_no_tags_given(self):
        # given
        parser.parse_args(['init'])
        parser.parse_args(['record', '--name', 'mongo1', '--command', 'mongo', '--tags', '#onduty,#mongo'])
        parser.parse_args(['record', '--name', 'mongo2', '--command', 'mongo'])

        with assert_stdout() as stdout:
            # when
            parser.parse_args(['list'])

            # then
            self.assertEqual(len(stdout.output), 2)
            self.assertOutputContains(stdout.output, 'mongo1: mongo')
            self.assertOutputContains(stdout.output, 'mongo2: mongo')

    @mock.patch('command_reminder.common.get_timestamp')
    def test_should_load_command_to_history_if_there_is_one_result(self, get_timestamp_mock):
        # given
        parser.parse_args(['init'])
        parser.parse_args(['record', '--name', 'mongo1', '--command', 'mongo dburl/dbname --username abc --password pass', '--tags', '#onduty,#mongo'])
        get_timestamp_mock.return_value = 1639436633

        # when
        parser.parse_args(['list'])

        # then
        history_file = os.path.join(TEST_PATH, '.local/share/fish/fish_history')
        with open(history_file, 'r') as f:
            content = ''.join([line for line in f.readlines()])
            self.assertEqual(content, f'''
- cmd brew install fish
  when 1639436632
- cmd mongo dburl/dbname --username abc --password pass
  when 1639436633
''')