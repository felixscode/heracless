# ⚔️ Heracless ⚔️

A simple and minimalistic Config Manager using YAML.   
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/felixscode/heracless)
[![PyPi](https://img.shields.io/badge/PyPi-Package-blue?logo=pypi)](https://pypi.org/project/heracless/)
[![Documentation](https://img.shields.io/badge/Documentation-Read-green?logo=readthedocs)](https://heracless.io/docs)
    

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Setup](#setup)
- [CLI Tool](#cli-tool)
- [Helper Functions in Heracless](#helper-functions-in-heracless)
  - [mutate_config](#mutate_config)
  - [as_dict](#as_dict)
  - [from_dict](#from_dict)
- [Version](#version)
- [Future](#future)
- [Author](#author)

## Description

Heracless aims to make working with config files in Python easy. It parses a config file into a dataclass and creates types as a Python stub file (.pyi) which can be used for type hints. Generated types also make autocompletion dreamy!

## Installation

Heracless is available as a pip package:

```bash
pip install heracless
```

If you want to build from source, run:

```bash
git clone https://github.com/felixscode/heracless.git
cd heracless
pip install -e .
```

## Setup

First, create a `config.yaml` file in a desired location and add desired configs. Make a new Python file called `load_config.py` and put it somewhere into your project.
Here is an example project structure:
```
├── src
│   └── your_module
│       ├── main.py
│       └──utils
│           └── load_config.py
├── data
│   └── config.yaml
├── README.md
├── pyproject.toml
└── .gitignore

```


Paste the following code into your `load_config.py`:

```python
from pathlib import Path
from typing import Type, TypeVar

from heracless import load_config as _load_config

# CONFIG_YAML_PATH is a global variable that sets the path of your YAML config file 
# Edit this to your config file path
CONFIG_YAML_PATH = None

Config = TypeVar("Config")

def load_config(frozen: bool = True) -> Config:
    """
    Load the configuration from the specified directory and return a Config object.

    Args:
        frozen (bool, optional): Whether the configuration should be frozen. Defaults to True.

    Returns:
        Config: The loaded configuration object.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML configuration file.

    Note:
        CONFIG_YAML_PATH is a global variable that sets the path of your YAML config file.
    """

    file_path = Path(__file__).resolve()
    yaml_config_path = CONFIG_YAML_PATH
    return _load_config(yaml_config_path,file_path, frozen=frozen)
```

After creating the `load_config.py` file, set the `CONFIG_YAML_PATH` variable to the path of your `config.yaml` file. For example:

```python
CONFIG_YAML_PATH = "/path/to/your/config.yaml"
```


## Helper Functions in Heracless

This document describes the helper functions in the `helper.py` module of the Heracless project.

### `mutate_config`

This function takes a `Config` object, a name, and a value, and returns a new `Config` object with the value at the name updated.

```python
from your_project import load_config

from heracless.utils.helper import mutate_config

config = load_config()
new_config = mutate_config(config, "name", "new_value")
```

### `as_dict`

This function converts a `Config` object to a dictionary.

```python
from your_project import load_config

from heracless.utils.helper import as_dict

config = load_config()
config_dict = as_dict(config)
```

### `from_dict`

This function creates a `Config` object from a dictionary. You can specify whether the `Config` object should be frozen.

```python
from heracless.utils.helper import from_dict

config_dict = {...}  # A dictionary representing the configuration
config = from_dict(config_dict, frozen=True)
```

## Version

Heracless 0.4 <br>
Written in Python 3.11

## Future

- [ ] Add config variants
- [ ] Add None type support
- [x] Web app

## Author

Felix Schelling<br>
GitHub: [felixscode](https://github.com/felixscode)<br>
Website: [heracless.io](https://heracless.io)<br>
Personal website: [felixschelling.de](https://felixschelling.de)<br>
Written with ❤️ in Mexico


