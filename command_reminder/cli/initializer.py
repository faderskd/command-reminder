from command_reminder.operations import processors
from command_reminder.config.config import Configuration


class AppContext:
    def __init__(self):
        self.config = Configuration.load_config()
        self.init_processor = processors.InitRepositoryProcessor()
        self.compound_processor = processors.CompoundProcessor([
            self.init_processor
        ])
