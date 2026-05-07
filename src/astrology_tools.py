"""
Astrology Tools API
====================
A simple callable interface to all astrology engine features.

Usage:
    from src.astrology_tools import AstrologyTools
    
    tools = AstrologyTools()
    chart = tools.calculate_chart(1996, 8, 13, 7, 18, "Fairfield", "CA")
    windows = tools.find_electional_window("Fairfield", "CA", "mercantile")
"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

# Ensure src is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT_DIR, ".env"))

from src.engine.calculator.main import calculate_chart_data
from src.engine.electional import ElectionalEngine
from src.engine.forensic_engine import Auditor
from src.engine.horary import build_horary_oracle
from src.engine.mundane import MundaneEngine

try:
    from src.api.v1.utils import result_to_model
except ImportError:
    # Fallback to reconstructing chart model directly if api utils are unavailable
    from src.engine.forensic_engine import Auditor

    result_to_model = Auditor._rebuild_chart_model


class AstrologyTools:
    """Unified interface to all astrology engine features."""

    def __init__(self):
        self.electional = ElectionalEngine()

    # =========================================================================
    # TOOL 1: CALCULATE CHART
    # =========================================================================
    def calculate_chart(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        city: str,
        state: str = "",
    ) -> Dict:
        """Calculate a natal chart for given birth data."""
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        time_str = f"{hour:02d}:{minute:02d}"
        return calculate_chart_data(date_str, time_str, city, state)

    # =========================================================================
    # TOOL 2: FORENSIC AUDIT
    # =========================================================================
    def forensic_audit(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        city: str,
        state: str = "",
    ) -> Dict:
        """Perform full practitioner-grade forensic audit."""
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        time_str = f"{hour:02d}:{minute:02d}"
        return Auditor.generate_full_nativity(
            date_str=date_str, time_str=time_str, city=city, state=state
        )

    # =========================================================================
    # TOOL 3: ELECTIONAL TIMING
    # =========================================================================
    def find_electional_window(
        self,
        city: str,
        state: str = "",
        activity: str = "general",
        hours_to_scan: int = 168,
        start_date: Optional[str] = None,
    ) -> Dict:
        """Find optimal timing windows for an activity."""
        start_dt = datetime.fromisoformat(start_date) if start_date else datetime.now()
        return self.electional.find_kairos(
            start_dt=start_dt,
            city=city,
            state=state,
            hours_to_scan=hours_to_scan,
            activity=activity,
        )

    # =========================================================================
    # TOOL 4: MUNDANE CONTEXT
    # =========================================================================
    def get_mundane_context(self, year: int, month: int = 1, day: int = 1) -> Dict:
        """Get mundane context: eclipses, great conjunctions, Firdaria."""
        import swisseph as swe

        jd = swe.julday(year, month, day, 12.0)
        engine = MundaneEngine(jd)
        return {
            "eclipses": engine.get_recent_eclipses(),
            "great_conjunction": engine.get_latest_great_conjunction(),
            "world_firdaria": engine.get_world_firdaria(),
            "mighty_firdaria": engine.get_mighty_firdaria(),
        }

    # =========================================================================
    # TOOL 5: HORARY ORACLE
    # =========================================================================
    def horary_judgment(
        self,
        question: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        city: str,
        state: str = "",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict:
        """Consult the Horary Oracle for a specific question."""
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        time_str = f"{hour:02d}:{minute:02d}"

        # Horary strictly uses Regiomontanus (R)
        res = calculate_chart_data(
            date_str,
            time_str,
            city,
            state,
            latitude=latitude,
            longitude=longitude,
            house_system="R",
        )
        if "error" in res:
            return res

        chart_model = result_to_model(res)
        return build_horary_oracle(question, chart_model)

    # =========================================================================
    # FORMATTED REPORTS
    # =========================================================================
    def format_electional_report(
        self, windows_data: Dict, natal_context: Optional[Dict] = None
    ) -> str:
        """
        Convert electional JSON data into a beautiful markdown report.
        """
        lines = []
        lines.append("# ⏰ ELECTIONAL TIMING REPORT")
        lines.append("")
        lines.append(
            f"**Location:** {windows_data.get('query', {}).get('location', 'Unknown')}"
        )
        lines.append(
            f"**Activity:** {windows_data.get('query', {}).get('activity', 'General').title()}"
        )
        lines.append(
            f"**Scan Period:** {windows_data.get('query', {}).get('scan_range', 'Unknown')}"
        )
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 🎯 TOP LAUNCH WINDOWS")
        lines.append("")

        for i, window in enumerate(windows_data.get("best_windows", [])[:5], 1):
            start = window.get("start", "")
            end = window.get("end", "")
            peak = window.get("peak_time", "")
            score = window.get("peak_score", 0)
            mood = window.get("mood", "Unknown")
            duration = window.get("duration_hours", 0)

            # Parse dates for nice formatting
            try:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                peak_dt = datetime.fromisoformat(peak)
                start_nice = start_dt.strftime("%b %d, %I:%M %p")
                end_nice = end_dt.strftime("%b %d, %I:%M %p")
                peak_nice = peak_dt.strftime("%b %d at %I:%M %p")
            except Exception:
                start_nice, end_nice, peak_nice = start, end, peak

            # Mood emoji
            mood_emoji = {
                "Excellent (Kairos)": "🌟",
                "Favorable": "✅",
                "Average": "⚖️",
                "Tenuous": "⚠️",
                "Dreadful": "❌",
            }.get(mood, "❓")

            lines.append(f"### Window #{i}: {mood_emoji} {mood}")
            lines.append("")
            lines.append(f"| Attribute | Value |")
            lines.append(f"|-----------|-------|")
            lines.append(f"| **Start** | {start_nice} |")
            lines.append(f"| **End** | {end_nice} |")
            lines.append(f"| **Peak Moment** | {peak_nice} |")
            lines.append(f"| **Duration** | {duration} hours |")
            lines.append(f"| **Score** | {score} |")
            lines.append("")

            details = window.get("details", [])
            if details:
                lines.append("**Astrological Factors:**")
                for detail in details:
                    lines.append(f"- {detail}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Add natal context if provided
        if natal_context:
            lines.append("## 📊 NATAL SYNCHRONIZATION")
            lines.append("")
            lines.append("Based on your natal chart:")
            lines.append("")
            if natal_context.get("almuten"):
                lines.append(f"- **Almuten Figuris:** {natal_context['almuten']}")
            if natal_context.get("time_lord"):
                lines.append(f"- **Current Time Lord:** {natal_context['time_lord']}")
            if natal_context.get("recommendations"):
                lines.append("")
                lines.append("**Recommendations:**")
                for rec in natal_context["recommendations"]:
                    lines.append(f"- {rec}")
            lines.append("")

        # Strategic guidance
        lines.append("## 📋 STRATEGIC GUIDANCE")
        lines.append("")
        lines.append("**Prioritize windows where:**")
        lines.append(
            "1. Mercury has positive Essential Dignity (+3 or higher) for mercantile activities"
        )
        lines.append("2. Moon is NOT Void of Course")
        lines.append("3. Ascendant Ruler is dignified or Cazimi")
        lines.append("4. Jupiter is angular (1st or 10th House)")
        lines.append("")
        lines.append("**Avoid:**")
        lines.append("- Mercury Retrograde periods")
        lines.append("- Combust Moon (within 8° of Sun)")
        lines.append("- Malefics (Mars/Saturn) on the Ascendant")
        lines.append("")
        lines.append("---")
        lines.append("*Generated by Kairos Electional Engine*")

        return "\n".join(lines)


# =============================================================================
# QUICK TEST
# =============================================================================
if __name__ == "__main__":
    tools = AstrologyTools()

    print("=" * 60)
    print("  ASTROLOGY TOOLS - QUICK TEST")
    print("=" * 60)

    # Test 1: Calculate Chart
    print("\n1. CALCULATE CHART")
    chart = tools.calculate_chart(1996, 8, 13, 7, 18, "Fairfield", "CA")
    print(f"   Chart calculated: {len(chart)} keys")

    # Test 2: Electional
    print("\n2. ELECTIONAL TIMING (48 hours)")
    windows = tools.find_electional_window(
        "Fairfield", "CA", "mercantile", hours_to_scan=48
    )
    if windows.get("best_windows"):
        print(f"   Found {len(windows['best_windows'])} windows")

        # Generate formatted report
        report = tools.format_electional_report(
            windows,
            natal_context={
                "almuten": "Mercury in Virgo (27 pts)",
                "time_lord": "Saturn Major → Mercury Sub-Period",
                "recommendations": [
                    "Launch during Mercury Sub-Period (Oct 2025 - Jun 2027)",
                    "Prioritize daytime launches (Diurnal Sect)",
                ],
            },
        )

        # Save formatted report
        with open(
            "chart_outputs/electional_launch_report.md", "w", encoding="utf-8"
        ) as f:
            f.write(report)
        print("   Saved formatted report to chart_outputs/electional_launch_report.md")

    # Test 3: Mundane
    print("\n3. MUNDANE CONTEXT")
    mundane = tools.get_mundane_context(2026, 2, 4)
    print(f"   Retrieved mundane data: {len(mundane)} sections")

    print("\n" + "=" * 60)
    print("  ALL TOOLS OPERATIONAL ✓")
    print("=" * 60)
