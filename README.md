# heracless

Config Manager using yaml.

# Description

heracless aims to make working with config files in python easy. It parses a config file into a dataclass
and creates types as a python file
with can be used for type hints. Generated types also make autocompletion a dreamy!

# Usage

first create a config file in yaml format and put in your desired fields.
to access the config information do like in following sample code.

```
from heracless import heracless
from config.types import Config

@heracless()
def main(cfg:Config) -> Any: 
"""
simply add a cfg parameter to any function at the first place
and access config attributes like you do any with any other object
"""
    some_sample_config_value = config.sample.some_value

```

its as simple as that!

or simply use the load_config function to load the config file into a dataclass
```
from heracless import load_config
from config.types import Config

@heracless()
def main(*args,**kwargs) -> Any: 
    config = load_config()
    print(config.sample.some_value)

```

arguments:

- **cfg_path**:Path yaml config file path -> Default ./config/config.yaml
- **dump_dir**:Path Path where types are going to be written to -> Default ./config/types.py
- **dump_func**:Callable control's the dumping behavior -> options: heracless.dump_in_file|heracless.dump_in_console| heracless.dump_dummy -> Default dump_in_file
- **frozen**:bool whether dataclass config objects are mutable or not -> Default True
- **make_dir**:bool make given paths or not if not existing -> Default True

# Cli-Tool

heracless also comes with a cli tool to generate the types file from a config file
simply run the following command in your terminal

```bash

heracless path/to/config.yaml -p path/to/types.py # generates types file
heracless path/to/config.yaml -d # dumps types to console
heracless path/to/config.yaml -h # for help
```
Sure, here's a markdown document that describes the functions in `helper.py` and provides example usage:

---

# Helper Functions in Heracless

This document describes the helper functions in the `helper.py` module of the Heracless project.

## `mutate_config`

This function takes a `Config` object, a name, and a value, and returns a new `Config` object with the value at the name updated.

```python
from heracless.utils.helper import mutate_config
from heracless.utils.c_types import Config

config = Config(...)  # Initialize a Config object
new_config = mutate_config(config, "name", "new_value")
```

## `as_dict`

This function converts a `Config` object to a dictionary.

```python
from heracless.utils.helper import as_dict
from heracless.utils.c_types import Config

config = Config(...)  # Initialize a Config object
config_dict = as_dict(config)
```

## `from_dict`

This function creates a `Config` object from a dictionary. You can specify whether the `Config` object should be frozen.

```python
from heracless.utils.helper import from_dict

config_dict = {...}  # A dictionary representing the configuration
config = from_dict(config_dict, frozen=True)
```

---

Remember to replace `Config(...)` and `{...}` with actual `Config` objects and dictionaries.

## installation

```bash
pip install heracless
```

## Version

heracless 0.2 <br>
written in python 3.11

## Future

add config variants <br>


## Author

Felix Schelling<br>
github: felixscode <br>
Witten with <3 in Mexico
