import os
from unittest import mock


from command_reminder.cli import parser
from command_reminder.config.config import COMMAND_REMINDER_DIR_ENV, HOME_DIR_ENV, REPOSITORIES_DIR_NAME, \
    MAIN_REPOSITORY_DIR_NAME, COMMANDS_FILE_NAME, FISH_FUNCTIONS_DIR_NAME, FISH_FUNCTIONS_PATH_ENV, \
    HISTORY_LOAD_FILE_NAME
from command_reminder.operations.common import InvalidArgumentException
from tests.common import BaseTestCase, assert_stdout
from tests.helpers import with_mocked_environment, TEST_TMP_DIR_PATH


@with_mocked_environment
class InitTestCase(BaseTestCase):

    def test_should_init_empty_github_repository(self):
        # when
        parser.parse_args(['init', '--repo', 'git@github.com:faderskd/command-reminder.git'])

        # then
        self.assertTrue(os.path.exists(
            f'/{TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{FISH_FUNCTIONS_DIR_NAME}'))
        self.assertTrue(os.path.exists(
            f'/{TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{COMMANDS_FILE_NAME}'))
        self.assertTrue(os.path.exists(os.path.join(TEST_TMP_DIR_PATH, REPOSITORIES_DIR_NAME, MAIN_REPOSITORY_DIR_NAME, ".git")))

    def test_should_init_directory_without_github_repository_given(self):
        # when
        parser.parse_args(['init'])

        # then
        self.assertTrue(os.path.exists(
            f'/{TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{FISH_FUNCTIONS_DIR_NAME}'))
        self.assertTrue(os.path.exists(
            f'/{TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{COMMANDS_FILE_NAME}'))
        self.assertFalse(os.path.exists(os.path.join(os.environ[COMMAND_REMINDER_DIR_ENV], ".git")))

    def test_should_return_init_script(self):
        # when
        with assert_stdout() as stdout:
            parser.parse_args(['init'])
            self.assertOutputContains(stdout.output,
                                      f'set -gx {FISH_FUNCTIONS_PATH_ENV} ${FISH_FUNCTIONS_PATH_ENV} {TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{FISH_FUNCTIONS_DIR_NAME}')

    @mock.patch.dict('os.environ', {COMMAND_REMINDER_DIR_ENV: TEST_TMP_DIR_PATH, HOME_DIR_ENV: ""})
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

    def test_should_create_alias_for_history_merge_command(self):
        # when
        parser.parse_args(['init'])

        # then
        alias_function = os.path.join(TEST_TMP_DIR_PATH, REPOSITORIES_DIR_NAME, MAIN_REPOSITORY_DIR_NAME,
                                      FISH_FUNCTIONS_DIR_NAME, HISTORY_LOAD_FILE_NAME)

        # and
        self.assertFileContent(alias_function, '''
function h
    cr load && history merge
end
''')
