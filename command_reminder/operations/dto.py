from dataclasses import dataclass


class OperationData: ...


@dataclass
class InitOperationDataDto(OperationData):
    repo: str
    directory: str
