import streamlit as st

st.set_page_config(page_title="Documentation", page_icon="📚")

st.markdown("# Documentation 📚")
st.sidebar.markdown("## Table of Contents")
st.sidebar.markdown(
    """
    - [Introduction](#introduction)
    - [Usage](#usage)
    - [Installation](#installation)
    - [Setup](#setup)
    - [Utils](#utils)
    - [Troubleshooting](#troubleshooting)
    """
)

st.markdown("## Introduction")
st.markdown(
    """
    Heracless is a simple and easy-to-use config manager for Python. It helps you manage your configuration files efficiently.
    """
)

st.markdown("## Usage")
st.markdown(
    """
    To use Heracless, you need to create a yaml configuration file and parse it using Heracless. Here is an example:

    ```yaml
    # config.yaml
    database:
      host: localhost
      port: 5432
      user: admin
    ```

    ```python
    from your_module import load_config

    config = load_config()
    print(config.database.host)  # Output: localhost
    ```
    """
)

st.markdown("## Installation")
st.markdown(
    """
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
"""
)
st.markdown("## Setup")
st.markdown(
    """
first, create a `config.yaml` file in a desired location and fill it with your configs. 
Make a new Python file called `load_config.py` and put it somewhere into your project.

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
    \"""
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
    \"""

    file_path = Path(__file__).resolve()
    yaml_config_path = CONFIG_YAML_PATH
    return _load_config(yaml_config_path,file_path, frozen=frozen)
```

After creating the `load_config.py` file, set the `CONFIG_YAML_PATH` variable to the path of your `config.yaml` file. For example:

```python
CONFIG_YAML_PATH = "/path/to/your/config.yaml"
```

import the `load_config` function from your module and your ready to rumble! 🚀
"""
)

st.markdown("## Utils")
st.markdown(
    """
### mutate config
mutate_config takes a `Config` object, a name, and a value, and returns a new `Config` object with the value at the name updated.

```python
from your_project import load_config
from heracless.utils.helper import mutate_config

config = load_config()
new_config = mutate_config(config, "name", "new_value")
```
**Note:** if frozzen is set to false you can simply overwrite the vale.

```python
from your_project import load_config
config = load_config()
config.some_value = "new_value"
```

### as_dict
as_dict converts a `Config` object to a dictionary.

```python
from your_project import load_config

from heracless.utils.helper import as_dict

config = load_config()
config_dict = as_dict(config)
```
### from_dict

from_dict creates a `Config` object from a dictionary. You can specify whether the `Config` object should be frozen.

```python
from heracless.utils.helper import from_dict

config_dict = {...}  # A dictionary representing the configuration
config = from_dict(config_dict, frozen=True)
```
"""
)
st.markdown("## Troubleshooting")
with st.expander("Autocompletion not working?"):
    st.markdown(
        """
        If autocompletion is not working, make sure:
        * reload the IDE.
        * IDE is configured to use the Python stub file (.pyi).
        * the Python stub file is in the same directory as your project.
        * the Python stub file has the same name as the Python file. 
        * the Python stub file has the `.pyi` extension.


        """
    )
with st.expander("File Errors?"):
    st.markdown(
        """
        If you get and os error, make sure:
        * the path to the config file is correct.
        * the config file exists.
        * the config file is not empty.
        * the config file is a valid yaml file.
        * generate the Python stub file via the [ConfigGenerator ⚡](heracless.io/ConfigGenerator).
        """
    )
with st.expander("Other Issues?"):
    st.markdown(
        """
        If you encounter other issues, please open an issue on the [GitHub repository](https://github.com/felixscode/heracless)
        """
    )
