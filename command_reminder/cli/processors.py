import typing

from command_reminder.operations.dto import OperationData
from command_reminder.operations.processors import Processor


class Operations:
    INIT = "init"
    RECORD = "record"
    LIST = "list"
    LOAD = "load"
    TAGS = "tags"
    REMOVE = "rm"


class CompoundProcessor:
    def __init__(self, processors: typing.List[typing.Tuple[str, Processor]]):
        self.processors = dict(processors)

    def process(self, operation_name: str, data: OperationData) -> None:
        self.processors[operation_name].process(data)