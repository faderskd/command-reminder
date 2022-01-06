from command_reminder.cli.parser import Operations
from command_reminder.cli.processors import CompoundProcessor
from command_reminder.operations import processors
from command_reminder.config.config import Configuration


class AppContext:
    def __init__(self):
        self.config = Configuration.load_config()
        self.init_processor = processors.InitRepositoryProcessor(self.config)
        self.record_processor = processors.RecordCommandProcessor(self.config)
        self.list_processor = processors.ListCommandsProcessor(self.config)
        self.load_processor = processors.LoadCommandProcessor(self.config)
        self.tags_processor = processors.TagsProcessor(self.config)
        self.remove_processor = processors.RemoveCommandProcessor(self.config)
        self.compound_processor = CompoundProcessor([
            (Operations.INIT, self.init_processor),
            (Operations.RECORD, self.record_processor),
            (Operations.LIST, self.list_processor),
            (Operations.LOAD, self.load_processor),
            (Operations.TAGS, self.tags_processor),
            (Operations.REMOVE, self.remove_processor)
        ])
