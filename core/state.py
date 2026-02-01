import streamlit as st


def init_session_state() -> None:
    defaults = {
        "api_key": "",
        "api_status": "",
        "chat_messages": [],
        "chat_pending_response": False,
        "consultant_short_mode": False,
        "swot_results": None,
        "consultant_file_context": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
