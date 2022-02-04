import os

from command_reminder.cli import parser
from command_reminder.config.config import REPOSITORIES_DIR_NAME, COMMANDS_FILE_NAME, FISH_FUNCTIONS_DIR_NAME, \
    EXTERNAL_REPOSITORIES_DIR_NAME, FISH_FUNCTIONS_PATH_ENV, MAIN_REPOSITORY_DIR_NAME
from tests.common import BaseTestCase, assert_stdout
from tests.helpers import with_mocked_environment, TEST_TMP_DIR_PATH


@with_mocked_environment
class PullExternalRepositoryTestCase(BaseTestCase):
    def test_should_pull_external_repository(self):
        # given
        parser.parse_args(['init'])

        # when
        parser.parse_args(['pull', '--repo', 'https://github.com/faderskd/common-commands'])

        # then
        external_commands_file = f'/{TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{EXTERNAL_REPOSITORIES_DIR_NAME}/faderskd_common_commands/{COMMANDS_FILE_NAME}'
        external_fish_function_file = f'/{TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{EXTERNAL_REPOSITORIES_DIR_NAME}/faderskd_common_commands/{FISH_FUNCTIONS_DIR_NAME}/external_command.fish'
        self.assertTrue(os.path.exists(external_commands_file))
        self.assertTrue(os.path.exists(external_fish_function_file))

    def test_should_generate_init_script_importing_main_and_external_repositories(self):
        # given
        parser.parse_args(['init'])
        parser.parse_args(['pull', '--repo', 'https://github.com/faderskd/common-commands'])

        with assert_stdout() as stdout:
            # when
            parser.parse_args(['init'])

            # then

            self.assertOutputContains(stdout.output,
                                      f'set -gx {FISH_FUNCTIONS_PATH_ENV} ${FISH_FUNCTIONS_PATH_ENV}'
                                      f' {TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{MAIN_REPOSITORY_DIR_NAME}/{FISH_FUNCTIONS_DIR_NAME}'
                                      f' {TEST_TMP_DIR_PATH}/{REPOSITORIES_DIR_NAME}/{EXTERNAL_REPOSITORIES_DIR_NAME}/faderskd_common_commands/{FISH_FUNCTIONS_DIR_NAME}')

    def test_should_list_external_commands_merged_with_main_commands(self):
        # given
        parser.parse_args(['init'])
        parser.parse_args(['pull', '--repo', 'https://github.com/faderskd/common-commands'])
        parser.parse_args(
            ['record', '--name', 'internal_command', '--command', 'some_internal_command'])

        with assert_stdout() as stdout:
            # when
            parser.parse_args(['list'])

            # then
            self.assertTrue(len(stdout.output), 2)
            self.assertOutputContains(stdout.output, 'internal_command: some_internal_command')
            self.assertOutputContains(stdout.output, 'external_command: some_external_command')

    def test_should_list_external_repos_tags_merge_with_main_tags(self):
        pass
