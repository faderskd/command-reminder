import os
from unittest import mock

from command_reminder.cli import parser
from tests.common import BaseTestCase
from tests.helpers import with_mocked_environment, TEST_TMP_DIR_PATH



@mock.patch('command_reminder.cli.parser.sys.stdin.readlines')
@mock.patch('command_reminder.common.get_timestamp')
@with_mocked_environment
class LoadCommandsListTestCase(BaseTestCase):

    def test_should_load_single_command_to_history(self, get_timestamp_mock, stdin_mock):
        # given
        get_timestamp_mock.return_value = 1639436633
        stdin_mock.return_value = ['mongo: dburl/dbname --username abc --password pass\n']

        # when
        parser.parse_args(['load'])

        # then
        history_file = os.path.join(TEST_TMP_DIR_PATH, '.local/share/fish/fish_history')
        self.assertFileContent(history_file, f'''
- cmd: brew install fish
  when: 1639436632
- cmd: dburl/dbname --username abc --password pass
  when: 1639436633
''')

    def test_should_load_multiple_commands_to_history(self, get_timestamp_mock, stdin_mock):
        # given
        get_timestamp_mock.return_value = 1639436633
        stdin_mock.return_value = [
            'mongo: dburl/dbname --username abc --password pass\n',
            'curl-local: curl http://localhost:8080\n',
            'ssh-machine: ssh somelogin@somemachine.domain.pl\n',
        ]

        # when
        parser.parse_args(['load'])

        # then
        history_file = os.path.join(TEST_TMP_DIR_PATH, '.local/share/fish/fish_history')
        self.assertFileContent(history_file, f'''
- cmd: brew install fish
  when: 1639436632
- cmd: dburl/dbname --username abc --password pass
  when: 1639436633
- cmd: curl http://localhost:8080
  when: 1639436633
- cmd: ssh somelogin@somemachine.domain.pl
  when: 1639436633
''')

