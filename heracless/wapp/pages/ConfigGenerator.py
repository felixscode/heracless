import streamlit as st
from streamlit_ace import st_ace
from streamlit_ace import THEMES
from heracless.wapp.utils import is_valid_yaml, get_file_content, download_button


st.set_page_config(page_title="ConfigGenerator", page_icon="⚡")


st.markdown("# Interactive Config Generator ⚡")
st.sidebar.header("Config Generator")
theme = st.sidebar.selectbox(
    "Editor Theme",
    options=THEMES,
    index=THEMES.index("xcode"),
)
config_dir = st.sidebar.text_input("Config Directory", value="../data/config.yaml")
load_file_name = st.sidebar.text_input("Load File Name", value="load_config.py")
frozen = st.sidebar.checkbox("Frozen (Immutable) Config", value=True)
st.write("""Enter your yaml config file below to generate a Python stub file (.pyi) for type hints. Enjoy!""")
content = st_ace(
    language="yaml",
    placeholder="Enter your yaml config file here...",
    height=300,
    theme=theme,
    keybinding="vscode",
    auto_update=True,
)
if st.button("Generate ⚡"):
    if is_valid_yaml(content):
        stub_string, template_str = get_file_content(content, config_dir, frozen)
        st.write("### Python Stub File")
        st.code(stub_string, language="python", line_numbers=True)
        download_button(label="Download 📥", data=stub_string, file_name=load_file_name.split(".")[0] + ".pyi")
        st.write("### Load Config Template")
        st.code(template_str, language="python")
        download_button(label="Download 📥", data=template_str, file_name=load_file_name)

    else:
        st.error("Invalid YAML content. Please check your input.")
