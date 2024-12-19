import streamlit as st

st.set_page_config(
    page_title="Heracless",
    page_icon="⚔️",
)


st.write("# ⚔️ Heracless ⚔️")

st.sidebar.success("Select Config Generator to see a demo.")

st.markdown(
    """
    [![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/felixscode/heracless)
    [![PyPi](https://img.shields.io/badge/PyPi-Package-blue?logo=pypi)](https://pypi.org/project/heracless/)
    [![Documentation](https://img.shields.io/badge/Documentation-Read-green?logo=readthedocs)](https://heracless.io/docs)
    

   
    A simple and easy-to-use config manager for Python.
    ## Description
    Heracless aims to make working with config files in Python easy. 
    It parses a yaml config file into a dataclass and creates types as a Python stub file (.pyi) which can be used for type hints. 
    Generated types also make autocompletion dreamy!
    ## Features
    - Parse yaml config files into a dataclass
    - Generate Python stub files (.pyi) for type hints
    - Autocompletion for generated types
    - Easy to use
    - Web App for interactive config generation
    - CLI interface
    ## Background
    Working with config files in Python can be a pain.
    There is metas Hydra, wich is a powerful tool for managing complex configurations.
    For simple projects, Hydra can be overkill. So I created Heracless, to fight Hydra.
    ## Installation
    ```bash
    pip install heracless
    ```
    ## About Stub Files
    Heracless generates Python stub files (.pyi) for type hints.
    Stub files are used by IDEs to provide autocompletion and type hints.
    Sub files where introduced in PEP 484 and are used by PyCharm, VSCode, and other IDEs.
    Readmore about stub files [here](https://www.python.org/dev/peps/pep-0484/#stub-files).
    ## License
    [MIT](https://github.com/aws/mit-0)
    ## Author
    Felix Schelling  
    GitHub: [felixscode](https://github.com/felixscode)  
    Website: [heracless.io](https://heracless.io)  
    Personal website: [felixschelling.de](https://felixschelling.de)  

    Written with ❤️ in Mexico
    """
)
