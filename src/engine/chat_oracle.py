import os
import json
import urllib.request
import urllib.error
import logging

logger = logging.getLogger(__name__)

import time

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED" 

    def allow_request(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"

_oracle_breaker = CircuitBreaker()

BINDER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Binder1.txt"))

def _load_binder_context():
    if not os.path.exists(BINDER_PATH):
        return ""
    try:
        with open(BINDER_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.warning("Error loading binder context: %s", repr(e), exc_info=True)
        return ""

BINDER_CONTEXT = _load_binder_context()

def _openrouter_request(messages, temperature, max_tokens, top_p=None):
    if not _oracle_breaker.allow_request():
        return "Error: Circuit Breaker Open (Too many failures). info: The Oracle is currently meditating (service unavailable)."
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: OPENROUTER_API_KEY environment variable not found. Please set it in your environment."

    try:
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
        # Default to Gemini 3 Pro for best reasoning with large context
        model = os.getenv("OPENROUTER_MODEL", "google/gemini-3-flash-preview")
        timeout = float(os.getenv("OPENROUTER_TIMEOUT", "120")) # Increased timeout for large context

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
        if top_p is not None:
            payload["top_p"] = top_p

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(base_url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw)

        if isinstance(result, dict) and "error" in result:
            _oracle_breaker.record_failure()
            err = result.get("error", {})
            msg = err.get("message") if isinstance(err, dict) else str(err)
            logger.warning("OpenRouter Error Payload: %s", result)
            return f"Oracle Communication Error: {msg}"

        choices = result.get("choices", []) if isinstance(result, dict) else []
        if not choices:
            _oracle_breaker.record_failure()
            logger.warning("OpenRouter result (no choices): %s", result)
            return "No response from engine."

        message = choices[0].get("message", {}) or {}
        content = message.get("content", "")
        # Support for Thinking Models (e.g. Gemini 2.0 Thinking, Gemini 3 Preview)
        # where output may be in 'reasoning'
        if not content and "reasoning" in message:
            content = message.get("reasoning", "")

        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    parts.append(part.get("text", ""))
                elif isinstance(part, str):
                    parts.append(part)
            content = "".join(parts)
            
        _oracle_breaker.record_success()
        return str(content).strip() or "No response from engine. (Note: Engine may have filtered content or produced empty reasoning)"
    except urllib.error.HTTPError as e:
        _oracle_breaker.record_failure()
        try:
            body = e.read().decode("utf-8")
            detail = json.loads(body)
            msg = detail.get("error", {}).get("message", body)
        except Exception as parse_err:
            logger.debug("Error body parse failed: %s", parse_err)
            msg = str(e)  # Use original HTTPError, not the parse error
        return f"Oracle Communication Error: {msg}"
    except Exception as e:
        _oracle_breaker.record_failure()
        return f"Oracle Communication Error: {str(e)}"

def get_chat_response(query: str, context: str) -> str:
    try:
        temperature = float(os.getenv("OPENROUTER_TEMPERATURE", "0.4"))
        max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "800"))
        # Default top_p to 0.9 for chat to allow some creativity but kept in check
        top_p = float(os.getenv("OPENROUTER_TOP_P", "0.9"))

        system_prompt = (
            "You are a highly advanced AI Astrology Oracle specializing in traditional Hellenistic and Medieval techniques. "
            "You have access to the 'Binder1.txt' source material for traditional astrology.\n\n"
            "SOURCE MATERIAL (Binder1.txt):\n"
            f"{BINDER_CONTEXT[:50000]}... (TRUNCATED FOR SYSTEM PROMPT)\n\n" # We'll handle full context in the user message for better attention
            "INSTRUCTIONS:\n"
            "1. Answer strictly based on the provided chart data and the traditional principles in the binder.\n"
            "2. Use a tone that is authoritative, slightly archaic/hermetic, yet precise and helpful.\n"
            "3. FRAMEWORK: Always frame your answers as traditional symbolic analysis."
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

        return _openrouter_request(messages, temperature, max_tokens, top_p=top_p)
    except Exception as e:
        return f"Oracle Communication Error: {str(e)}"

def explain_reading_in_plain_terms(reading_context: str, tier: str = 'free') -> str:
    context = (reading_context or "").strip()
    if not context:
        return ""

    # Increase max chars to handle the binder better if passed in turn 1
    max_chars = int(os.getenv("PLAIN_READING_MAX_CHARS", "100000"))
    if len(context) > max_chars:
        context = context[:max_chars]

    temperature = float(os.getenv("OPENROUTER_PLAIN_TEMPERATURE", "0.2"))
    max_tokens = int(os.getenv("OPENROUTER_PLAIN_MAX_TOKENS", "8000")) # Expanded for high-volume dossiers
    top_p = float(os.getenv("OPENROUTER_PLAIN_TOP_P", "0.85"))

    system_prompt = (
        "You are a master plain-language astrology interpreter and expert in the 'Binder1.txt' source material. "
        "Your goal is to provide a massive, 20-page style detailed analysis of the provided chart. "
        "Use second-person language ('you'). Maintain a professional, deep, and slightly authoritative tone. "
        "Do NOT compress your knowledge. Be exhaustive."
    )

    if tier == 'free':
        # Free Tier: Single iteration
        questions = [
            f"Explain the user's Natural Temperament and Core Character based on this data and the Binder1 context. Keep it under 300 words.\n\nCHART DATA:\n{context}"
        ]
    else:
        # Paid Tier: High-Volume Multi-Module Interrogation
        questions = [
            f"REFERENCE MATERIAL (Binder1.txt):\n{BINDER_CONTEXT}\n\nCHART DATA:\n{context}\n\nTASK (Turn 1): Provide a foundational interpretation of core character, temperament, and soul architecture. Aim for at least 800 words, going into extreme detail on the hierarchies of causation.",
            "TASK (Turn 2): Deep-dive into Professional & Social Destiny. Analyze career, wealth, and public status based on the Lot of Fortune, MC, and relevant ministers. Provide at least 800 words of tactical analysis.",
            "TASK (Turn 3): Deep-dive into the Private Soul & Psychology. Analyze fears, hidden assets, and the subconscious houses (12th, 8th, 4th). Provide at least 800 words on the internal architecture.",
            "TASK (Turn 4): Deep-dive into Relationships, Love, and Social Dynamics. Analyze partner choice and major interpersonal patterns. Aim for 800 words of relational mapping.",
            "TASK (Turn 5): Forecasting & Universal Override. Analyze major upcoming triggers (2025-2030) and the interaction between natal particulars and universal causes. Provide 800 words of temporal mapping.",
            "FINAL TASK: Synthesize the entire conversation into a massive, cohesive, premium Dossier for the customer. This MUST be a comprehensive manuscript (aiming for 5,000+ words). Use clear chapters, elaborate on every point discussed, and do not summarize. We need the full volume of your knowledge for this practitioner-grade report."
        ]

    messages = [{"role": "system", "content": system_prompt}]
    responses = []

    responses = []
    
    # We use a token-efficient "chaining" pattern to avoid hitting daily limits.
    # Turns 2-5 only see the Chart Data and the PREVIOUS answer.
    # Turn 6 (Synthesis) sees all intermediate answers.
    
    chart_data_only = f"CHART DATA:\n{context}"
    
    for i, question in enumerate(questions):
        logger.info("Turn %d of %d...", i+1, len(questions))
        
        if i == 0:
            # Turn 1: Full Binder + Full Chart Data
            current_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        elif i < len(questions) - 1:
            # Intermediate Turns: Chart Data + Previous Answer
            current_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chart_data_only},
                {"role": "assistant", "content": responses[-1]},
                {"role": "user", "content": question}
            ]
        else:
            # Final Synthesis: Aggregate all answers
            current_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "The following are deep-dive analyses performed on the chart data. Synthesize them into the final dossier."}
            ]
            for j, resp in enumerate(responses):
                current_messages.append({"role": "user", "content": f"Module {j+1} Analysis: {resp}"})
            current_messages.append({"role": "user", "content": question})

        response = _openrouter_request(current_messages, temperature, max_tokens, top_p=top_p)
        
        if not response or response.startswith("Oracle Communication Error") or response.startswith("Error:"):
            if len(responses) == 0:
                return response or "Unknown Error"
            break
            
        responses.append(response)

    # Return the final synthesized document
    return responses[-1].strip()

