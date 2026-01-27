import google.generativeai as genai
import os

def get_chat_response(query: str, context: str) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY environment variable not found. Please set it in your environment."

    try:
        genai.configure(api_key=api_key)
        
        # User requested "Gemini 3 Flash", mapping to "gemini-1.5-flash" (latest flash)
        model = genai.GenerativeModel('gemini-3-flash')
        
        prompt = f"""You are the 'Codex Caelestis', a highly advanced AI Astrology Oracle. 
You have generated a detailed 'Forensic Audit' of a natal chart.
The user is asking a question about this specific reading.

CONTEXT (The Reading):
{context}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Answer strictly based on the provided chart data.
2. Use a tone that is authoritative, slightly archaic/hermetic, yet precise and helpful.
3. If the reading doesn't contain the answer, say so, but offer a hypothesis based on general astrological principles if applicable (differentiating it from the hard data).
4. Keep answers concise but insightful.

ANSWER:"""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Oracle Communication Error: {str(e)}"
