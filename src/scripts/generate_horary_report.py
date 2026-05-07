"""
CLI script to generate a horary astrology report.
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Ensure src is in the python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

# pylint: disable=wrong-import-position
from src.astrology_tools import AstrologyTools


def main():
    """
    Main entry point for generating a horary request from the CLI.
    """
    parser = argparse.ArgumentParser(description="Generate a Horary report")
    parser.add_argument(
        "--question", required=True, type=str, help="The question being asked"
    )
    parser.add_argument(
        "--date", required=True, type=str, help="Date in YYYY-MM-DD format"
    )
    parser.add_argument("--time", required=True, type=str, help="Time in HH:MM format")
    parser.add_argument("--city", required=True, type=str, help="City of the querent")
    parser.add_argument(
        "--state", default="", type=str, help="State/country of the querent"
    )

    args = parser.parse_args()

    try:
        dt = datetime.strptime(f"{args.date} {args.time}", "%Y-%m-%d %H:%M")
    except ValueError as e:
        print(f"Error parsing date/time: {e}")
        sys.exit(1)

    tools = AstrologyTools()
    result = tools.horary_judgment(
        question=args.question,
        year=dt.year,
        month=dt.month,
        day=dt.day,
        hour=dt.hour,
        minute=dt.minute,
        city=args.city,
        state=args.state,
    )

    if "error" in result:
        print(f"Error executing horary judgment: {result['error']}")
        sys.exit(1)

    # Inject Safety Disclaimer (Operational Constraint)
    disclaimer = (
        "Historical Use Only: This horary judgment is for historical "
        "astrological research only and does not constitute medical, "
        "financial, or legal advice."
    )
    result["disclaimer"] = disclaimer

    # Print the JSON output
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
