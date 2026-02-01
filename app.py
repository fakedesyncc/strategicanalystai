import streamlit as st

from core.config import APP_TITLE, PAGE_ICON
from core.state import init_session_state
from ui.styles import load_custom_css
from ui.header import render_header
from ui.sidebar import render_sidebar
from ui.consultant_tab import render_consultant_tab
from ui.swot_tab import render_swot_tab

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
load_custom_css()
render_header()

api_key, model = render_sidebar()

tab_consultant, tab_swot = st.tabs(["Консультант", "SWOT-Анализ"])

with tab_consultant:
    render_consultant_tab(api_key, model)

with tab_swot:
    render_swot_tab(api_key, model)
