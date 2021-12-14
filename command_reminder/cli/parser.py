import re
import sys
import argparse
from argparse import ArgumentParser

from command_reminder.operations.dto import InitOperationDto, RecordCommandOperationDto, ListOperationDto
from command_reminder.config.config import DEFAULT_REPOSITORY_DIR

from command_reminder.cli.initializer import AppContext


class Operations:
    INIT = "init"
    RECORD = "record"
    LIST = "list"


def parse_args(raw_args) -> None:
    app_context = AppContext()
    parser = define_parser()
    args = parser.parse_args(raw_args)
    operation = args.operation

    if operation == Operations.INIT:
        app_context.compound_processor.process(InitOperationDto(repo=args.repo))
    elif operation == Operations.RECORD:
        app_context.compound_processor.process(RecordCommandOperationDto(
            command=args.command, name=args.name, tags=re.split('[\\s,]+', args.tags)))
    elif operation == Operations.LIST:
        app_context.compound_processor.process(
            ListOperationDto(tags=re.split('[\\s,]+', args.tags) if args.tags else []))
    else:
        parser.print_help()


def define_parser():
    parser = argparse.ArgumentParser(description='Command Reminder CLI')
    subparsers = parser.add_subparsers(help="Command Reminder command to execute", dest="operation")
    init_parser = subparsers.add_parser(Operations.INIT, description="Initializes command-reminder project")
    record_parser = subparsers.add_parser(Operations.RECORD, description="Adds command to registry")
    list_parser = subparsers.add_parser(Operations.LIST, description="Adds command to registry")
    _init_subparser(init_parser)
    _record_subparser(record_parser)
    _list_subparser(list_parser)
    return parser


def _init_subparser(parser: ArgumentParser) -> None:
    parser.add_argument('-r', '--repo', type=str, default="",
                        help=f'Repository to which saving commands. If empty default "~/{DEFAULT_REPOSITORY_DIR}" will be used')


def _record_subparser(parser: ArgumentParser) -> None:
    parser.add_argument('-n', '--name', type=str,
                        help='Name of the command. It will be used to reference it during different operations.')
    parser.add_argument('-t', '--tags', type=str, default="",
                        help='Tags to search command for.')
    parser.add_argument('-c', '--command', type=str,
                        help='Command to record')


def _list_subparser(parser: ArgumentParser) -> None:
    parser.add_argument('-t', '--tags', type=str,
                        help='Tags to search commands for.', default="")


if __name__ == '__main__':
    sys.argv[0] = "command-reminder"
    parse_args(sys.argv[1:])
