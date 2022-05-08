# command-reminder
Command reminder is a tool for saving and sharing your mostly used fish shell commands. It allows quickly add 
commands to a local database, which can then be persisted/shared via Github.

# Prerequisites
```
python >= 3.9
``` 

# Installation
```bash
> pip install command-reminder
```

# Quickstart
1. Create a Github repo which will then serve as your commands' database. Use this repo to init a new project. 

    ```bash 
    > cr init --repo git@github.com:mygithubuser/my-command-reminder-repository.git
   ```  

    It will create a `~/.command-reminder` directory, where all your commands will exist. You can change that directory by
    setting `COMMAND_REMINDER_DIR` variable.
    
2. Add `cr init | source` to the `~/.config/fish/config.fish` file. Every time you start the fish shell,
   it will load both default and saved fish functions.
   
3. Record a command.  

    ```bash
    > cr record --name 'lsof_listening_ports' --command 'lsof -nP -iTCP:$PORT | grep LISTEN'
   ```  
     
   Remember to use `'` except `"` whenever a command contains `$` sign, otherwise the environment variable will be resolved.
   It saves a command to the local database. You can use tags too:  

   ```bash
   > cr record --name 'show_process_rss_memory' --command 'ps o pid,rss -p 23159' --tags '#memory #process'
   ```
   The record command creates a fish function too (available at shell after running `cr init | source`). It allows to quickly get
   autosuggestions about available commands just by entering few first command's letters and typing `Tab`. Currently, it only
   prints the command.
   
4. List all available commands.  

    `> cr list` or `> cr list --pretty`
   
   ```bash
   lsof_listening_ports: lsof -nP -iTCP:$PORT | grep LISTEN
   show_process_rss_memory: ps o pid,rss -p 23159
   git_pull: git pull --rebase
   ```
    
   Narrow down the results to the specific tag.  
   
   ```bash
   > cr list --tags '#memory'
   ```
   
5. Load a command to the shell. It would be very inconvenient to copy and paste the listed command. Command reminder
   comes with a useful shortcut, which loads commands to the fish history - they are available just by typing `arrow up`.
   
   ```bash
   > cr list | grep ps | h 
   ```
 
   The `h` shortcut is a function which name is derived from "history". It loads the command to the fish history. Remember to
   add it to a fish via `cr init | source`. Press the `arrow up` and you can execute a found result as a usual command.  
   
6. Push recorded commands to the remote repository.
   ```bash
   > cr push
   ```  
   
7. You can pull external repositories too. Let's say you're working with a team of a few people and have
   a common set of commands, useful in your working environment. More experienced team members can share their
   commands to the new ones.
   
   ```bash
   > cr pull -r git@github.com:somegithubuser/some-external-commands-repository.git
   ```
   
   The `pull` command adds given repository to the configuration file: `~/.command-reminder/repositories/main/config.yaml`,
   which is then saved in the Github repo together with the recorded commands. On any machine with access to your Github repo (and external too),
   you just init a new project and provide the proper URL. You will have downloaded your own commands as well as the external ones.
   To refresh the commands from external repositories use:
   
   ```bash
   > cr pull -update_all
   ```
8. The main help menu is available via: `cr --help`. Each subcommand supports help as well, e.g. `cr init --help`.

# Repository structure
```
~/.command-reminder/
    repositories/
        main/
            commands.json
            fish/
            config.yaml
        external/
            ext1/
                commands.json
                fish/
            ext2/
                commands.json
                fish/
``` 

* The `main` directory is a place where all your commands are kept. 
* Configuration file `config.yaml` contains data to restore your commands anywhere command-reminder is installed:
    ```
    repositories:
      external:
        - url: ...
        - url: ...
    ```
* `commands.json` keeps recorded commands
* `fish` directory keeps fish functions for commands. It is added to your fish search path (via `cr init | source`), 
so all commands are available as a function with fish autosuggestions. For now, the fish functions just print the respective command.
* The `external` directory contains external repositories' commands.

# Development

#### Install deps  
```bash
> pipenv install --dev
> source .venv/bin/activate.fish
```
#### Test
```bash
> tox
```

#### Publish
```bash
> python setup.py sdist
> twine check dist/*
> twine upload dist/*
```

#### Installation from local setup.py
```bash
> pip install .
```

# QA:  
**1. I've got problems with pushing changes to remote repository:**  
The push command use `git` shell command underneath. You can just go to the main directory and push it manually.
