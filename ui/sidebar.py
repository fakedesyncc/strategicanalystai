from typing import Tuple

import streamlit as st

from core.config import DEFAULT_MODEL, MODELS
from modules.api_handler import check_connection


def render_sidebar() -> Tuple[str, str]:
    st.sidebar.markdown("### Настройки API")
    st.sidebar.markdown("---")
    api_key = st.sidebar.text_input(
        "API ключ OpenRouter",
        value=st.session_state.get("api_key", ""),
        type="password",
        placeholder="sk-or-v1-...",
    )
    st.session_state["api_key"] = api_key
    model = st.sidebar.selectbox(
        "Модель",
        MODELS,
        index=MODELS.index(DEFAULT_MODEL) if DEFAULT_MODEL in MODELS else 0,
    )
    if st.sidebar.button("Проверить подключение", use_container_width=True):
        if api_key:
            ok, msg = check_connection(api_key, model)
            if ok:
                st.session_state["api_status"] = "Подключено"
                st.sidebar.success(msg)
            else:
                st.session_state["api_status"] = "Ошибка"
                st.sidebar.error(msg)
        else:
            st.sidebar.error("Введите API ключ")
    if st.session_state.get("api_status"):
        st.sidebar.caption(f"Статус: {st.session_state['api_status']}")
    st.sidebar.markdown("---")
    consultant_mode = st.sidebar.radio(
        "Ответ консультанта",
        ["Развёрнутый", "Короткий (для сессии)"],
        index=0,
        help="Короткий — несколько строчек, удобно на стратегической сессии.",
    )
    st.session_state["consultant_short_mode"] = consultant_mode == "Короткий (для сессии)"
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Режимы работы")
    st.sidebar.markdown("**Консультант** — диалог с аналитиком для разбора ситуаций.")
    st.sidebar.markdown("**SWOT-Анализ** — массовая оценка тезисов с выгрузкой в Excel и Word.")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "### Подсказки\n\n"
        "Загружайте до 100 тезисов за раз. Форматы: TXT, XLSX, CSV, DOCX. "
        "Результаты можно выгрузить в Word и Excel."
    )
    return api_key, model
