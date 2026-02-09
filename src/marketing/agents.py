import json
from datetime import datetime
from src.agents.main import AstroAgent
from src.marketing.tools import split_into_thread

class MarketingAgent:
    """
    Agent responsible for generating high-ticket astrology marketing content.
    """
    def __init__(self):
        self.astro_agent = AstroAgent()
    
    def get_current_transits(self) -> dict:
        """Calculates chart for the current moment to find hooks."""
        now = datetime.now()
        # default to a generic location (e.g., UTC/Greenwich or just New York)
        # using New York for "market" relevance or just standard
        data = self.astro_agent.calculate(
            now.strftime("%Y-%m-%d"), 
            now.strftime("%H:%M"), 
            "New York", 
            "NY"
        )
        return data

    def generate_hook(self, topic: str) -> str:
        """
        Generates a compelling hook for a topic.
        In a real scenario, this would call an LLM.
        For now, we return template hooks based on the strategy.
        """
        hooks = {
            "sect": "Most apps ignore Sect. But it's 50% of your chart's power. Day vs Night matters. ☀️🌙",
            "profections": "Who is the Lord of your Year? Annual Profections unlock your 2024 theme. 🔑",
            "firdaria": "Your life isn't random. It's governed by Time Lords. Firdaria shows you the chapter you're in. 📖",
            "medical": "Medical Astrology is specific. Salt, digestion, headache? Look at the Moon and 6th House. ⚕️"
        }
        return hooks.get(topic.lower(), f"Unlock the ancient wisdom of your chart with {topic}.")

    def generate_thread(self, topic: str, chart_context: dict = None) -> list[str]:
        """
        Generates a thread about a specific topic.
        """
        if topic.lower() == "saturn in pisces":
             content = (
                "Saturn in Pisces is not just 'hardship'. It's about structuring the intangible. "
                "1. If you have Pisces rising, Saturn is in your 1st House. You are redefining your identity. "
                "2. If Virgo rising, it's your 7th House. Relationships are being tested for reality. "
                "3. Use this time to build a container for your dreams. "
                "Our engine can calculate exactly how this hits your chart based on your unique Sect and bounds."
             )
        else:
            content = f"Deep dive into {topic}. Traditional astrology offers forensic accuracy. We analyze every degree, every dignity. Don't settle for generic horoscopes."

        return split_into_thread(content)

    def run_daily_content_gen(self):
        """Generates a set of options for the day."""
        transits = self.get_current_transits()
        moon_sign = "Unknown" # extraction logic would go here from 'transits'
        
        # Simplified logic for demo
        return {
            "hook": self.generate_hook("sect"),
            "thread": self.generate_thread("Saturn in Pisces")
        }
