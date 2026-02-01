import streamlit as st


def render_header() -> None:
    status = st.session_state.get("api_status") or "не проверен"
    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-header-brand">
                <span class="app-header-logo">Strategic Analyst AI</span>
            </div>
            <div class="app-header-status">Статус API: {status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
