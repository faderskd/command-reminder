import re
import sys
import argparse
from argparse import ArgumentParser

from command_reminder.cli.processors import Operations
from command_reminder.config.config import DEFAULT_REPOSITORY_DIR

from command_reminder.cli.initializer import AppContext
from command_reminder.operations.init_repository import InitOperationDto
from command_reminder.operations.list_commands import ListOperationDto
from command_reminder.operations.load_command import LoadCommandsListDto
from command_reminder.operations.pull_external_repo import PullExternalRepositoryDto
from command_reminder.operations.record_command import RecordCommandOperationDto
from command_reminder.operations.remove_command import RemoveCommandDto

TAGS_SPLITTER = '[\\s,]+'
NAME_REPLACER = '[\\s+-]'


def parse_args(raw_args) -> None:
    app_context = AppContext()
    parser = define_parser()
    args = parser.parse_args(raw_args)
    operation = args.operation

    if operation == Operations.INIT:
        app_context.compound_processor.process(operation, InitOperationDto(repo=args.repo))
    elif operation == Operations.RECORD:
        app_context.compound_processor.process(operation, RecordCommandOperationDto(
            command=args.command, name=re.sub(NAME_REPLACER, '_', args.name), tags=re.split(TAGS_SPLITTER, args.tags)))
    elif operation == Operations.LIST:
        app_context.compound_processor.process(operation, ListOperationDto(
            tags=re.split(TAGS_SPLITTER, args.tags) if args.tags else [], pretty=args.pretty))
    elif operation == Operations.LOAD:
        app_context.compound_processor.process(operation, LoadCommandsListDto(commands=sys.stdin.readlines()))
    elif operation == Operations.TAGS:
        app_context.compound_processor.process(operation, None)
    elif operation == Operations.REMOVE:
        app_context.compound_processor.process(operation, RemoveCommandDto(command_name=args.command))
    elif operation == Operations.PULL:
        app_context.compound_processor.process(operation, PullExternalRepositoryDto(repo=args.repo, refresh_all=args.update_all))
    elif operation == Operations.PUSH:
        app_context.compound_processor.process(operation, None)
    else:
        parser.print_help()


def define_parser():
    parser = argparse.ArgumentParser(description='Command Reminder CLI')
    subparsers = parser.add_subparsers(help="Command Reminder command to execute", dest="operation")
    init_parser = subparsers.add_parser(Operations.INIT, description='Initializes command-reminder project')
    record_parser = subparsers.add_parser(Operations.RECORD, description='Adds command to registry')
    list_parser = subparsers.add_parser(Operations.LIST, description='Adds command to registry')
    remove_parser = subparsers.add_parser(Operations.REMOVE, description="Removes a command")
    subparsers.add_parser(Operations.LOAD, description='Loads command to history')
    subparsers.add_parser(Operations.TAGS, description='Lists available tags')
    pull_subparser = subparsers.add_parser(Operations.PULL, description='Pulls external commands repository')
    subparsers.add_parser(Operations.PUSH, description='Pushes changes to main repository')
    _init_subparser(init_parser)
    _record_subparser(record_parser)
    _list_subparser(list_parser)
    _remove_subparser(remove_parser)
    _pull_subparser(pull_subparser)
    return parser


def _init_subparser(parser: ArgumentParser) -> None:
    parser.add_argument('-r', '--repo', type=str, default='',
                        help=f'Repository to which save commands. If empty default "~/{DEFAULT_REPOSITORY_DIR}" will be used')


def _record_subparser(parser: ArgumentParser) -> None:
    parser.add_argument('-n', '--name', type=str,
                        help='Name of the command. It will be used to reference it during different operations.',
                        required=True)
    parser.add_argument('-t', '--tags', type=str, default='',
                        help='Tags to search command for.')
    parser.add_argument('-c', '--command', type=str,
                        help='Command to record', required=True)


def _list_subparser(parser: ArgumentParser) -> None:
    parser.add_argument('-t', '--tags', type=str,
                        help='Tags to search commands for.', default='')
    parser.add_argument('-p', '--pretty', action='store_true')


def _remove_subparser(parser: ArgumentParser) -> None:
    parser.add_argument('-c', '--command', type=str,
                        help='Command name to remove.', required=True)


def _pull_subparser(parser: ArgumentParser) -> None:
    parser.add_argument('-r', '--repo', type=str,
                        help='Pulls external commands repository.', required=False)
    parser.add_argument('-ua', '--update_all',
                        help='Refreshes all external repositories,', action='store_true')


if __name__ == '__main__':
    sys.argv[0] = 'command-reminder'
    parse_args(sys.argv[1:])
