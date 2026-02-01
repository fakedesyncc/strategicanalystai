import time
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_RETRIES = 3
INITIAL_DELAY = 1.0
TIMEOUT = 30


def check_connection(api_key: str, model: str) -> tuple[bool, str]:
    if not api_key or not api_key.strip():
        return False, "Введите API ключ"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Ответь одним словом: OK"}
        ],
        "max_tokens": 10,
        "temperature": 0,
    }
    try:
        r = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=15,
        )
        if r.status_code == 401:
            return False, "Неверный API ключ"
        if r.status_code == 429:
            return False, "Превышен лимит запросов. Попробуйте позже."
        if r.status_code != 200:
            return False, f"Ошибка API: {r.status_code} — {r.text[:200]}"
        return True, "Подключение успешно"
    except requests.exceptions.Timeout:
        return False, "Таймаут. Проверьте интернет и повторите."
    except requests.exceptions.RequestException as e:
        return False, f"Ошибка сети: {str(e)}"


def chat_completion(
    api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> tuple[bool, str]:
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    delay = INITIAL_DELAY
    last_error = ""
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=TIMEOUT,
            )
            if r.status_code == 401:
                return False, "Неверный API ключ"
            if r.status_code == 429:
                last_error = "Превышен лимит запросов. Попробуйте позже."
                time.sleep(delay)
                delay *= 2
                continue
            if r.status_code != 200:
                return False, f"Ошибка API: {r.status_code} — {r.text[:300]}"
            data = r.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            return True, content.strip()
        except requests.exceptions.Timeout:
            last_error = "Таймаут запроса"
            time.sleep(delay)
            delay *= 2
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            time.sleep(delay)
            delay *= 2
    return False, last_error or "Не удалось выполнить запрос"


def chat_completion_with_history(
    api_key: str,
    model: str,
    system_prompt: str,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> tuple[bool, str]:
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    payload = {
        "model": model,
        "messages": full_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    delay = INITIAL_DELAY
    last_error = ""
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=TIMEOUT,
            )
            if r.status_code == 401:
                return False, "Неверный API ключ"
            if r.status_code == 429:
                last_error = "Превышен лимит запросов. Попробуйте позже."
                time.sleep(delay)
                delay *= 2
                continue
            if r.status_code != 200:
                return False, f"Ошибка API: {r.status_code} — {r.text[:300]}"
            data = r.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            return True, content.strip()
        except requests.exceptions.Timeout:
            last_error = "Таймаут запроса"
            time.sleep(delay)
            delay *= 2
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            time.sleep(delay)
            delay *= 2
    return False, last_error or "Не удалось выполнить запрос"
