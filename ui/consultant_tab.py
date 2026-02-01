from datetime import datetime

import streamlit as st

from core.config import (
    MAX_CONTEXT_CHARS,
    CHAT_MAX_TOKENS,
    CHAT_MAX_TOKENS_SHORT,
    CHAT_PLACEHOLDER_MESSAGE,
)
from modules.api_handler import chat_completion_with_history
from modules.prompts import CONSULTANT_SYSTEM, CONSULTANT_SYSTEM_SHORT
from modules.export_utils import export_chat_txt, export_chat_md, export_chat_docx
from services.file_parser import read_uploaded_file_as_text
from ui.chat_ui import build_chat_html


def render_consultant_tab(api_key: str, model: str) -> None:
    st.markdown("## Консультант-аналитик")
    st.caption("Свободный диалог для анализа ситуаций. Прикрепите файл к полю ввода при необходимости.")

    messages = st.session_state.get("chat_messages", [])
    pending = st.session_state.get("chat_pending_response", False)

    if pending and messages:
        last = messages[-1]
        if last.get("role") == "assistant" and last.get("content") == CHAT_PLACEHOLDER_MESSAGE:
            history_for_api = messages[:-1]
            short = st.session_state.get("consultant_short_mode", False)
            system = CONSULTANT_SYSTEM_SHORT if short else CONSULTANT_SYSTEM
            max_tokens = CHAT_MAX_TOKENS_SHORT if short else CHAT_MAX_TOKENS
            with st.spinner("Анализирую..."):
                ok, reply = chat_completion_with_history(
                    api_key,
                    model,
                    system,
                    history_for_api,
                    max_tokens=max_tokens,
                )
            st.session_state["chat_pending_response"] = False
            if ok:
                st.session_state["chat_messages"] = history_for_api + [
                    {"role": "assistant", "content": reply}
                ]
            else:
                st.session_state["chat_messages"] = history_for_api
                st.error(reply)
            st.rerun()

    st.markdown(build_chat_html(messages), unsafe_allow_html=True)

    # Блок «файл + поле ввода» — визуально один блок
    st.markdown(
        '<div class="chat-input-block" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    with st.expander("Прикрепить файл к сообщению", expanded=False):
        consultant_file = st.file_uploader(
            "Перетащите сюда или нажмите",
            type=["txt", "csv", "xlsx", "xls", "docx"],
            key="consultant_upload",
        )
        if consultant_file:
            st.session_state["consultant_file_context"] = read_uploaded_file_as_text(
                consultant_file, max_chars=MAX_CONTEXT_CHARS
            )
            st.caption(f"Файл «{consultant_file.name}» прикреплён и будет учтён при отправке.")
        else:
            st.session_state["consultant_file_context"] = ""

    user_input = st.chat_input("Опишите ситуацию для анализа...")

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Очистить историю", key="clear_chat"):
            st.session_state["chat_messages"] = []
            st.session_state["chat_pending_response"] = False
            st.rerun()
    with c2:
        st.download_button(
            "Скачать TXT",
            data=export_chat_txt(messages) if messages else "",
            file_name=f"dialog_{ts}.txt",
            mime="text/plain",
            key="dl_chat_txt",
            disabled=not messages,
        )
    with c3:
        st.download_button(
            "Скачать MD",
            data=export_chat_md(messages) if messages else "",
            file_name=f"dialog_{ts}.md",
            mime="text/markdown",
            key="dl_chat_md",
            disabled=not messages,
        )
    with c4:
        st.download_button(
            "Выгрузить в Word (DOCX)",
            data=export_chat_docx(messages) if messages else b"",
            file_name=f"dialog_{ts}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_chat_docx",
            disabled=not messages,
        )

    if not user_input:
        return

    context = st.session_state.get("consultant_file_context", "")
    full_user_message = user_input
    if context:
        full_user_message = (
            f"Контекст из прикреплённого файла:\n\n{context}\n\n"
            f"---\nВопрос/ситуация:\n{user_input}"
        )

    st.session_state["chat_messages"] = st.session_state.get("chat_messages", []) + [
        {"role": "user", "content": full_user_message}
    ]

    if not api_key:
        st.error("Введите API ключ в боковой панели и нажмите «Проверить подключение».")
        st.session_state["chat_messages"] = st.session_state["chat_messages"][:-1]
        return

    st.session_state["chat_messages"] = st.session_state["chat_messages"] + [
        {"role": "assistant", "content": CHAT_PLACEHOLDER_MESSAGE}
    ]
    st.session_state["chat_pending_response"] = True
    st.rerun()
