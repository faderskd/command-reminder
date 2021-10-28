from command_reminder.cmd_processors import processors

init_processor = processors.InitRepositoryProcessor()
compound_processor = processors.CompoundProcessor([
    init_processor
])
