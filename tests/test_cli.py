import unittest
from unittest.mock import patch, MagicMock

from command_reminder.cli import parser
from command_reminder.cmd_processors.dto import InitOperationDto


@patch('command_reminder.cli.parser.get_compound_processor')
class CliParserTestCase(unittest.TestCase):
    def test_should_init_repository(self, get_compound_processor: MagicMock):
        # given
        get_compound_processor.return_value = processor_mock = MagicMock()

        # when
        parser.parse_args(['init', '--repo', 'https://github.com/faderskd/command-reminder'])

        # then
        processor_mock.process.assert_called_once_with(
            InitOperationDto('https://github.com/faderskd/command-reminder'))

    def test_should_init_repository_with_default_value(self, get_compound_processor: MagicMock):
        # given
        get_compound_processor.return_value = processor_mock = MagicMock()

        # when
        parser.parse_args(['init'])

        # then
        processor_mock.process.assert_called_once_with(InitOperationDto(parser.DEFAULT_REPOSITORY_REPO))
