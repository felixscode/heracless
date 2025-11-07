from pathlib import Path
from typing import Any

import yaml
import streamlit as st

from heracless.fight import load_as_dict, tree_parser, tree_to_config_obj, tree_to_string_translator
from heracless.utils.utils import insert_path_into_load_config_template


def is_valid_yaml(content: str) -> bool:
    try:
        yaml.safe_load(content)
        return True
    except yaml.YAMLError as e:
        return False


def get_file_content(yaml_content: str, relative_path: Path, frozen: bool) -> tuple[str, str]:
    cfg_dict: Any = yaml.safe_load(yaml_content)
    if cfg_dict is None:  # in case dict is empty and config
        return "", ""
    cfg_tree = tree_parser(cfg_dict)
    stub_string = tree_to_string_translator(frozen, cfg_tree)
    template_str = insert_path_into_load_config_template(relative_path)
    return stub_string, "".join(template_str)


@st.fragment
def download_button(label: str, data: str, file_name: str) -> None:
    st.download_button(label=label, data=data, file_name=file_name, mime="text/x-python")
