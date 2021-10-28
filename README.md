# command-reminder
Tool for saving/sharing your mostly used commands for fish shell

# Installation
pip install command-reminder

# Usage

#### Create new repository

> cr init
> cr init --repo "git@github.com:faderskd/command-reminder.git"

#### Record useful commands

> cr record "mongo dburl/dbname --username abc --password pass"
>
> cr record --tags "#sed #macosx" "sed -i '' -e 's/source/target/g'" file.txt

#### Show commands
> cr show --tags #sed

#### Show tags
> cr tags

### Save changes to remote
> cr push

#### Add external repository
> cr repo add git@github.com:faderskd/command-reminder-network.git

# Configuration
```editorconfig
[REPOSITORY]
Url = git@github.com:faderskd/command-reminder.git
Path = ~/.command-reminder
``` 