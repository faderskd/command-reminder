import json
import typing


def read_file_content(f) -> typing.Dict[str, typing.List[typing.List[str]]]:
    s = f.read()
    if not s:
        commands = {}
    else:
        commands = json.loads(s)
    return commands
