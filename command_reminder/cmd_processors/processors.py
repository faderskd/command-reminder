import typing

from command_reminder.cmd_processors.dto import Operation, InitOperationDto


class InvalidArgumentException(ValueError):
    pass


class Processor:
    def process(self, operation: Operation):
        pass


class InitRepositoryProcessor(Processor):

    def process(self, data: Operation) -> None:
        if not isinstance(data, InitOperationDto):
            return
        self._validate(data)

    @staticmethod
    def _validate(data: InitOperationDto):
        if not data.repo:
            raise InvalidArgumentException("Repository cannot be empty")


class CompoundProcessor:
    def __init__(self, processors: typing.List[Processor]):
        self.processors = processors

    def process(self, operation: Operation):
        for p in self.processors:
            p.process(operation)
