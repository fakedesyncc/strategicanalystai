import re


def _escape(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _content_to_html(content: str) -> str:
    if not content:
        return ""
    s = _escape(content)
    lines = s.split("\n")
    out = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if re.match(r"^###\s+", stripped):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(re.sub(r"^###\s+(.+)$", r"<h3 class=\"chat-h3\">\1</h3>", stripped))
        elif re.match(r"^##\s+", stripped) and not stripped.startswith("###"):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(re.sub(r"^##\s+(.+)$", r"<h2 class=\"chat-h2\">\1</h2>", stripped))
        elif re.match(r"^#\s+", stripped) and not stripped.startswith("##"):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(re.sub(r"^#\s+(.+)$", r"<h1 class=\"chat-h1\">\1</h1>", stripped))
        elif stripped in ("---", "***", "___"):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("<hr class=\"chat-hr\">")
        elif re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            if not in_list:
                out.append("<ul class=\"chat-ul\">")
                in_list = True
            if re.match(r"^[-*]\s+", stripped):
                out.append(re.sub(r"^[-*]\s+(.+)$", r"<li>\1</li>", stripped))
            else:
                out.append(re.sub(r"^\d+\.\s+(.+)$", r"<li>\1</li>", stripped))
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            if stripped:
                out.append(line)
            else:
                out.append("<br>")
    if in_list:
        out.append("</ul>")
    s = "\n".join(out)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code class=\"chat-code\">\1</code>", s)
    s = s.replace("\n", "<br>")
    return s


def build_chat_html(messages: list[dict]) -> str:
    if not messages:
        return (
            '<div class="chat-static-container">'
            '<div class="chat-empty">Начните диалог — опишите ситуацию в поле ниже.</div>'
            "</div>"
        )
    parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = _content_to_html(msg.get("content", ""))
        if role == "user":
            parts.append(
                f'<div class="chat-msg chat-msg-user">'
                f'<span class="chat-msg-role">Вы</span>'
                f'<div class="chat-msg-content">{content}</div>'
                f"</div>"
            )
        else:
            parts.append(
                f'<div class="chat-msg chat-msg-assistant">'
                f'<span class="chat-msg-role">Аналитик</span>'
                f'<div class="chat-msg-content">{content}</div>'
                f"</div>"
            )
    return (
        '<div class="chat-static-container">'
        + "\n".join(parts)
        + "</div>"
    )
