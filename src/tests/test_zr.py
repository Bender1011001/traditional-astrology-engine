from datetime import datetime

from src.engine.models import Sign
from src.engine.prediction import calculate_zr_lifetime_map


def test_zr():
    start_sign = Sign.PISCES
    birth_date = datetime(1990, 1, 1)

    chapters = calculate_zr_lifetime_map(start_sign, birth_date, years=50)

    print(f"Total Chapters: {len(chapters)}")
    for i, ch in enumerate(chapters):
        print(
            f"Chapter {i+1}: {ch['sign']} ({ch['duration_years']} years) | {ch['start_date']} to {ch['end_date']}"
        )
        # Print a few paragraphs
        for p in ch["paragraphs"][:3]:
            print(
                f"  - {p['sign']} | {p['start_date']} to {p['end_date']} | {p['status']}"
            )
        print("  ...")


if __name__ == "__main__":
    test_zr()
