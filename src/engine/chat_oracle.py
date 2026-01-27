import google.generativeai as genai
import os

def get_chat_response(query: str, context: str) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY environment variable not found. Please set it in your environment."

    try:
        genai.configure(api_key=api_key)
        
        # User requested "Gemini 3 Flash", mapping to "gemini-1.5-flash" (latest flash)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are an astrological interpreter grounded in traditional sources.
You have generated a detailed forensic audit of a natal chart.
The user is asking a question about this specific reading.

CONTEXT (The Reading):
{context}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Answer strictly from the provided chart data. Do not add external theory or guesses.
2. Use direct, matter-of-fact statements in plain modern language (2025 tone).
3. Provide a little more detail when the data supports it, but do not invent anything.
4. If the data does not contain the answer, say: "No rule for this in the provided data."
5. Prefer declarative statements like "You are", "You have", "You will" when supported by the data.
6. When citing support, reference exact data points (dignity, sect, house, condition).
7. Keep it concise.

ANSWER:"""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Engine Error: {str(e)}"
