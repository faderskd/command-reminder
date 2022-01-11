import os

from command_reminder.cli import parser
from command_reminder.config.config import REPOSITORIES_DIR_NAME, COMMANDS_FILE_NAME, FISH_FUNCTIONS_DIR_NAME, \
    EXTERNAL_REPOSITORIES_DIR_NAME
from tests.common import BaseTestCase
from tests.helpers import with_mocked_environment, TEST_PATH

@with_mocked_environment
class PullExternalRepositoryTestCase(BaseTestCase):
    def test_should_pull_external_repository(self):
        # given
        parser.parse_args(['init'])

        # when
        parser.parse_args(['pull https://github.com/faderskd/common-commands'])

        # then
        external_commands_file = f'/{TEST_PATH}/{REPOSITORIES_DIR_NAME}/{EXTERNAL_REPOSITORIES_DIR_NAME}/faderskd_common_commands/{COMMANDS_FILE_NAME}'
        external_fish_function_file = f'/{TEST_PATH}/{REPOSITORIES_DIR_NAME}/{EXTERNAL_REPOSITORIES_DIR_NAME}/faderskd_common_commands/{FISH_FUNCTIONS_DIR_NAME}/external_cmd.fish'
        self.assertTrue(os.path.exists(external_commands_file))
        self.assertTrue(os.path.exists(external_fish_function_file))

    # def test_should_generate_init_script_importing_

    def test_should_list_external_commands_merged_with_main_commands(self):
        pass