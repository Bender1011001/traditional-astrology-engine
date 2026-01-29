import os
import json
import urllib.request
import urllib.error

def _openrouter_request(messages, temperature, max_tokens):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: OPENROUTER_API_KEY environment variable not found. Please set it in your environment."

    try:
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
        model = os.getenv("OPENROUTER_MODEL", "google/gemini-3-flash-preview")
        timeout = float(os.getenv("OPENROUTER_TIMEOUT", "30"))

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        site_url = os.getenv("OPENROUTER_SITE_URL", "").strip()
        app_name = os.getenv("OPENROUTER_APP_NAME", "").strip()
        if site_url:
            headers["HTTP-Referer"] = site_url
        if app_name:
            headers["X-Title"] = app_name

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(base_url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw)

        if isinstance(result, dict) and "error" in result:
            err = result.get("error", {})
            msg = err.get("message") if isinstance(err, dict) else str(err)
            return f"Oracle Communication Error: {msg}"

        choices = result.get("choices", []) if isinstance(result, dict) else []
        if not choices:
            return "No response from engine."

        message = choices[0].get("message", {}) or {}
        content = message.get("content", "")
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    parts.append(part.get("text", ""))
                elif isinstance(part, str):
                    parts.append(part)
            content = "".join(parts)
        return str(content).strip() or "No response from engine."
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")
            detail = json.loads(body)
            msg = detail.get("error", {}).get("message", body)
        except Exception:
            msg = str(e)
        return f"Oracle Communication Error: {msg}"
    except Exception as e:
        return f"Oracle Communication Error: {str(e)}"

def get_chat_response(query: str, context: str) -> str:
    try:
        temperature = float(os.getenv("OPENROUTER_TEMPERATURE", "0.4"))
        max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "800"))

        system_prompt = (
            "You are the 'Codex Caelestis', a highly advanced AI Astrology Oracle. "
            "You have generated a detailed 'Forensic Audit' of a natal chart. "
            "The user is asking a question about this specific reading.\n\n"
            "INSTRUCTIONS:\n"
            "1. Answer strictly based on the provided chart data.\n"
            "2. Use a tone that is authoritative, slightly archaic/hermetic, yet precise and helpful.\n"
            "3. If the reading doesn't contain the answer, say so, but offer a hypothesis based on general astrological principles if applicable (differentiating it from the hard data).\n"
            "4. Keep answers concise but insightful.\n"
            "5. FRAMEWORK: Always frame your answers as traditional symbolic analysis, not deterministic physical prediction. Use phrases like 'The tradition suggests...', 'Symbolically, this indicate...', or 'In the grammar of the heavens...'."
        )

        user_prompt = (
            "CONTEXT (The Reading):\n"
            f"{context}\n\n"
            "USER QUESTION:\n"
            f"{query}\n\n"
            "ANSWER:"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return _openrouter_request(messages, temperature, max_tokens)
    except Exception as e:
        return f"Oracle Communication Error: {str(e)}"

def explain_reading_in_plain_terms(reading_context: str) -> str:
    context = (reading_context or "").strip()
    if not context:
        return ""

    max_chars = int(os.getenv("PLAIN_READING_MAX_CHARS", "12000"))
    if len(context) > max_chars:
        context = context[:max_chars]

    temperature = float(os.getenv("OPENROUTER_PLAIN_TEMPERATURE", os.getenv("OPENROUTER_TEMPERATURE", "0.4")))
    max_tokens = int(os.getenv("OPENROUTER_PLAIN_MAX_TOKENS", os.getenv("OPENROUTER_MAX_TOKENS", "800")))

    system_prompt = (
        "You are a plain-language astrology interpreter. "
        "Explain the reading in everyday terms for a general audience while going into as much detail as possible. "
        "Make the explanation very understandable, concrete, and grounded in the provided material. "
        "Use second-person language and favor frequent \"you\" statements. "
        "Avoid jargon. If you must use a technical term, define it in one short clause. "
        "Use short paragraphs, clear cause-and-effect phrasing, and a calm, practical tone. "
        "Do not mention you are an AI and do not mention JSON. "
        "IMPORTANT: Always maintain a probabilistic and symbolic tone. Avoid saying 'You will X' or 'This means Y will happen'. Instead, use 'This suggests a theme of X' or 'The traditional archetypes point toward Y'."
    )

    questions = [
        f"Explain this in regular terms:\n\n{context}",
        "what else can you tell me?",
        "what else",
        "anything else?",
        "is that all?"
    ]

    messages = [{"role": "system", "content": system_prompt}]
    responses = []

    for question in questions:
        messages.append({"role": "user", "content": question})
        response = _openrouter_request(messages, temperature, max_tokens)
        if not response or response.startswith("Oracle Communication Error") or response.startswith("Error:"):
            return ""
        responses.append(response)
        messages.append({"role": "assistant", "content": response})

    return "\n\n".join(r for r in responses if r).strip()
