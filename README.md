# Title Belt Calculator

Finds the shortest path to having a shot at the belt for a given team and belt holder.

## Setup

```
poetry install

# either open a poetry shell to run everything
poetry shell

# or run individual commands with the poetry run prefix
poetry run title-belt-nhl`
```

The following steps assume you are in a poetry shell.
Add `poetry run ` at the beginning of commands if not.

## Usage

Run with `title-belt-nhl`.

```
$ title-belt-nhl --help

Usage: title-belt-nhl [OPTIONS]

Options:
  --team TEXT    [required]
  --season TEXT
  --help         Show this message and exit.

Commands:
  path
  path-alt
```

* use `path-alt` to get a string showing list of games
* use `path` to get the list of games using a diff algorithm

## Linting and Formatting

### Linting

`ruff check title_belt_nhl`

#### Fix Lint Errors

`ruff check --fix title_belt_nhl`

### Formatting

`ruff format title_belt_nhl`

#### Autoformat on save (vscode)

1. Install `ruff` extension
1. Update settings in `.vscode/settings.json`:
    ```
    {
        "[python]": {
          "editor.formatOnSave": true,
          "editor.defaultFormatter": "charliermarsh.ruff",
          "editor.codeActionsOnSave": {
            "source.fixAll": "explicit"
          }
        }
    }
    ```
1. Ensure you are using the python interpreter from the poetry shell.
    - Open command palette (Ctrl+Shift+P)
    - `Python: Select Interpreter`
    - "Select at workspace level"
    - "Enter interpreter path"
    - Copy/paste the path to your poetry virtualenv
      - Run `poetry env info` and copy the path to the Executable under **Virtualenv**
      - Should be something like `/home/user/.cache/pypoetry/virtualenvs/title-belt-nhl-asdf1234-py3.10/bin/python`
  
    -  When you open a python file in vscode, the bottom right corner of the window should show something like:
        ```
        Python  3.10.14 ("title-belt-nhl-asdf1234-py3.10": poetry)
        ```

## Testing

Run `poetry run pytest` to run through any tests in the `./title_belt_nhl/tests` folder
