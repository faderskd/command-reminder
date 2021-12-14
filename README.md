# command-reminder
Tool for saving/sharing your mostly used commands for fish shell

# Installation
pip install command-reminder

# Usage

#### Create new repository

> cr init
> cr init --repo "git@github.com:faderskd/command-reminder.git"

#### Record useful commands

> cr record  --name "mongo_login" --command "mongo dburl/dbname --username abc --password pass"
>
> cr record --name "sed" --tags "#sed #macosx" --command "sed -i '' -e 's/source/target/g' file.txt"

#### Show commands
> cr show --tags #sed

#### Show tags
> cr tags

### Save changes to remote
> cr push

#### Add external repository
> cr repo add git@github.com:faderskd/command-reminder-network.git

#### Configuration
```editorconfig
[REPOSITORY]
ConfigDir = ~/.command-reminder
``` 

#### Publish
```
python setup.py sdist
twine check dist/*
twine upload dist/*
```

#### Installation from local setup.py
```
pip install .
```

#### Repository structure
```
~/.command-reminder/
    config
    repositories/
        main/
            commands.txt
            fish/
        extensions/
            ext1/
                commands.txt
                fish/
            ext1/
            ...
``` 