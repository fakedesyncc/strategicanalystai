import re
from typing import Optional

import pandas as pd


def strip_markdown_for_display(text: str) -> str:
    if not text:
        return ""
    s = str(text).strip()
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    s = re.sub(r"__([^_]+)__", r"\1", s)
    s = re.sub(r"_([^_]+)_", r"\1", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def verdict_badge_class(verdict: Optional[str]) -> str:
    v = (verdict or "").strip().upper()
    if "ПРОДВИГАТЬ" in v:
        return "badge-success"
    if "ДОРАБОТАТЬ" in v:
        return "badge-warning"
    if "ОТКЛОНИТЬ" in v or "ОШИБКА" in v:
        return "badge-danger"
    return ""


def escape_html(value) -> str:
    s = str(value) if value is not None else ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_results_table_html(df: pd.DataFrame) -> str:
    rows_html = []
    for idx, r in df.iterrows():
        thesis = strip_markdown_for_display(r.get("Тезис", ""))
        effect = strip_markdown_for_display(r.get("Эффект", ""))
        risks = strip_markdown_for_display(r.get("Риски", ""))
        verdict = strip_markdown_for_display(r.get("Вердикт", ""))
        badge = verdict_badge_class(verdict)
        verdict_cell = (
            f'<span class="{badge}">{escape_html(verdict)}</span>'
            if badge
            else escape_html(verdict)
        )
        rows_html.append(
            f"<tr>"
            f"<td class=\"col-num\">{idx + 1}</td>"
            f"<td class=\"col-text\">{escape_html(thesis)}</td>"
            f"<td class=\"col-text\">{escape_html(effect)}</td>"
            f"<td class=\"col-text\">{escape_html(risks)}</td>"
            f"<td class=\"col-verdict\">{verdict_cell}</td>"
            f"</tr>"
        )
    return """
    <div class="results-table-wrap">
    <table class="results-table">
    <thead>
    <tr>
    <th>№</th><th>Тезис</th><th>Эффект</th><th>Риски</th><th>Вердикт</th>
    </tr>
    </thead>
    <tbody>
    """ + "\n".join(rows_html) + """
    </tbody>
    </table>
    </div>
    """
