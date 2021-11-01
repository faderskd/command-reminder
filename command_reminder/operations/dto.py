import typing
from dataclasses import dataclass


class OperationData: ...


@dataclass
class InitOperationDataDto(OperationData):
    repo: str


@dataclass
class RecordCommandOperationDataDto(OperationData):
    command: str
    name: str
    tags: typing.List[str]
