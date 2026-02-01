from datetime import datetime

import pandas as pd
import streamlit as st

from core.config import SWOT_UPLOAD_TYPES
from modules.api_handler import chat_completion
from modules.prompts import SWOT_TEMPLATES
from modules.export_utils import (
    parse_swot_response,
    export_swot_xlsx,
    export_swot_csv,
    export_swot_md,
    export_swot_docx,
)
from services.file_parser import parse_theses_from_text, parse_theses_from_upload
from services.swot_ui import build_results_table_html


def render_swot_tab(api_key: str, model: str) -> None:
    st.markdown("## SWOT-анализатор предложений")
    st.caption("Массовый анализ списка тезисов. Ввод: текст или загрузка файла.")

    st.markdown("**Шаг 1. Загрузка данных**")
    input_mode = st.radio(
        "Способ ввода",
        ["Текстовый ввод", "Загрузка файла"],
        horizontal=True,
        key="swot_input_mode",
    )
    theses_list = []
    if input_mode == "Текстовый ввод":
        raw_text = st.text_area(
            "Тезисы (каждый с новой строки)",
            height=150,
            placeholder="Введите тезисы, каждый с новой строки...",
            key="swot_text",
            label_visibility="collapsed",
        )
        theses_list = parse_theses_from_text(raw_text or "")
    else:
        swot_file = st.file_uploader(
            "Перетащите файл сюда или выберите файл (.txt, .csv, .xlsx)",
            type=SWOT_UPLOAD_TYPES,
            key="swot_file",
        )
        if swot_file:
            theses_list = parse_theses_from_upload(swot_file)
            if theses_list:
                st.success(
                    f"Загружен файл «{swot_file.name}». Найдено тезисов: {len(theses_list)}"
                )
            else:
                st.warning(
                    f"Файл «{swot_file.name}» загружен, но тезисы не найдены. "
                    "Проверьте формат: один тезис на строку или один столбец в таблице."
                )

    st.markdown("**Шаг 2. Настройки анализа**")
    prompt_template = st.selectbox(
        "Шаблон промта", list(SWOT_TEMPLATES.keys()), key="swot_template"
    )
    custom_prompt = st.text_area(
        "Кастомный системный промт (оставьте пусто, чтобы использовать шаблон)",
        height=80,
        key="swot_custom",
    )
    system_prompt = (
        custom_prompt.strip() if custom_prompt.strip() else SWOT_TEMPLATES[prompt_template]
    )

    if st.button("Начать анализ", key="run_swot", type="primary"):
        if not theses_list:
            st.warning("Добавьте хотя бы один тезис.")
        elif not api_key:
            st.error("Введите API ключ в боковой панели и проверьте подключение.")
        else:
            _run_swot_analysis(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                theses_list=theses_list,
            )

    swot_results = st.session_state.get("swot_results")
    if swot_results:
        st.markdown("**Шаг 3. Результаты**")
        df = pd.DataFrame(swot_results)
        verdicts = [v for v in df["Вердикт"].dropna().unique().tolist() if v]
        filter_verdict = st.multiselect(
            "Фильтр по вердикту",
            verdicts,
            default=verdicts,
            key="swot_filter",
        )
        df_f = df[df["Вердикт"].isin(filter_verdict)] if filter_verdict else df
        st.markdown(build_results_table_html(df_f), unsafe_allow_html=True)

        st.markdown("**Выгрузка результатов**")
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        ex1, ex2, ex3, ex4 = st.columns(4)
        with ex1:
            st.download_button(
                "Выгрузить в Excel (XLSX)",
                data=export_swot_xlsx(df_f),
                file_name=f"swot_analysis_{ts}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_xlsx",
            )
        with ex2:
            st.download_button(
                "Выгрузить в Word (DOCX)",
                data=export_swot_docx(df_f),
                file_name=f"swot_analysis_{ts}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="dl_docx",
            )
        with ex3:
            st.download_button(
                "Скачать CSV",
                data=export_swot_csv(df_f),
                file_name=f"swot_analysis_{ts}.csv",
                mime="text/csv",
                key="dl_csv",
            )
        with ex4:
            st.download_button(
                "Скачать Markdown",
                data=export_swot_md(df_f),
                file_name=f"swot_analysis_{ts}.md",
                mime="text/markdown",
                key="dl_md",
            )


def _run_swot_analysis(
    api_key: str,
    model: str,
    system_prompt: str,
    theses_list: list,
) -> None:
    st.session_state["swot_results"] = []
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    table_placeholder = st.empty()
    n = len(theses_list)
    for i, thesis in enumerate(theses_list):
        status_placeholder.caption(f"Обработка: {i + 1} из {n}")
        progress_bar.progress((i + 1) / n)
        ok, content = chat_completion(
            api_key,
            model,
            system_prompt,
            thesis,
            temperature=0.5,
            max_tokens=600,
        )
        row = parse_swot_response(thesis, content if ok else content)
        if not ok:
            row["Вердикт"] = "Ошибка"
            row["Эффект"] = content[:200]
        st.session_state["swot_results"].append(row)
        df_so_far = pd.DataFrame(st.session_state["swot_results"])
        table_placeholder.dataframe(df_so_far, width="stretch", hide_index=True)
    progress_bar.empty()
    status_placeholder.empty()
    st.success("Анализ завершён.")
    st.rerun()
