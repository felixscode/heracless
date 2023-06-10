# heracless

Config Manager using yaml.

## Description

heracless aims to make working with config files in python easy. It parses a config file into a dataclass
and creates types as a python file
with can be used for type hints. Generated types also make autocompletion a dreamy!

## Usage

first create a config file in yaml format and put in your desired fields.
to access the config information do like in following sample code.

```
from heracless.decorator import heracless
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

Decorator arguments:

- **cfg_path**:Path yaml config file path -> Default ./config/config.yaml
- **dump_dir**:Path Path where types are going to be written to -> Default ./config/types.py
- **dump_func**:Callable control's the dumping behavior -> options: heracless.dump_in_file|heracless.dump_in_console| heracless.dump_dummy -> Default dump_in_file
- **frozen**:bool whether dataclass config objects are mutable or not -> Default True
- **make_dir**:bool make given paths or not if not existing -> Default True

## installation

```bash
pip install heracless
```

## Version

heracless 0.1 <br>
written in python 3.11

## Future

add clitool<br>
add config variants <br>
add ray wrapper for hyperparameter optimization configs

## Author

Felix Schelling<br>
github: felixscode <br>
Witten with <3 in Mexico
