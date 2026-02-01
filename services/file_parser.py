import io
from typing import List, Optional

import pandas as pd


def parse_theses_from_text(text: Optional[str]) -> List[str]:
    if not text or not text.strip():
        return []
    return [line.strip() for line in text.strip().split("\n") if line.strip()]


def parse_theses_from_upload(uploaded_file) -> List[str]:
    name = (uploaded_file.name or "").lower()
    try:
        raw = uploaded_file.read()
        if name.endswith(".txt"):
            return parse_theses_from_text(raw.decode("utf-8", errors="replace"))
        if name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig", header=None)
            if len(df.columns) > 0:
                return [str(x).strip() for x in df.iloc[:, 0].dropna() if str(x).strip()]
            return []
        if name.endswith(".xlsx") or name.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(raw), header=None)
            if len(df.columns) > 0:
                return [str(x).strip() for x in df.iloc[:, 0].dropna() if str(x).strip()]
            return []
    except Exception:
        pass
    return []


def read_uploaded_file_as_text(uploaded_file, max_chars: int = 8000) -> str:
    name = (uploaded_file.name or "").lower()
    try:
        raw = uploaded_file.read()
        if name.endswith(".txt"):
            out = raw.decode("utf-8", errors="replace")
            return out[:max_chars] if len(out) > max_chars else out
        if name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig")
            return df.to_string()[:max_chars]
        if name.endswith(".xlsx") or name.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(raw))
            return df.to_string()[:max_chars]
        if name.endswith(".docx"):
            from docx import Document
            doc = Document(io.BytesIO(raw))
            out = "\n".join(p.text for p in doc.paragraphs)
            return out[:max_chars] if len(out) > max_chars else out
    except Exception:
        pass
    return ""
