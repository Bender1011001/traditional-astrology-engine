import asyncio


from src.engine.calculator.main import calculate_chart_data
from src.engine.synthesis import ReportSynthesizer


async def test_options():
    print("--- Testing Node Type Option ---")
    # 1. Mean Node (Default)
    data_mean = calculate_chart_data(
        date_str="2023-01-01", time_str="12:00", city="London", node_type="mean"
    )
    mean_node_lon = data_mean["planets"]["North_Node"]["longitude"]
    print(f"Mean Node Longitude: {mean_node_lon}")

    # 2. True Node
    data_true = calculate_chart_data(
        date_str="2023-01-01", time_str="12:00", city="London", node_type="true"
    )
    true_node_lon = data_true["planets"]["North_Node"]["longitude"]
    print(f"True Node Longitude: {true_node_lon}")

    if abs(mean_node_lon - true_node_lon) > 0.001:
        print("✅ SUCCESS: Mean and True Node longitudes differ.")
    else:
        print("❌ FAILURE: Mean and True Node longitudes are identical.")

    print("\n--- Testing Peregrine Labeling ---")
    # Date where Sun is likely Peregrine?
    # Sun in Libra (Fall) - Not Peregrine.
    # Sun in Aquarius (Detriment) - Not Peregrine.
    # Sun in Taurus usually has no dignity (Peregrine) unless in Term/Face.
    # Let's try Sun in Taurus ~15 deg (May 5th)
    # Day chart -> Triplicity? Earth: Venus (Day), Moon (Night), Mars (Part). Sun has no trip.
    # Terms?
    # Taurus Egyptian Terms: Ven(8), Mer(14), Jup(22), Sat(27), Mar(30).
    # Sun at 15 is in Jupiter Term.
    # We need a spot where the planet has NO dignity.
    # Sun in Gemini (Air): Trip Sat/Mer/Jup.
    # Sun in Gemini 5 deg. Ruler Mer. Exalt Node (not Sun). Trip: Sat(D). Term: Mer(6). Face: Jup.
    # Peregrine is hard to find for Sun sometimes due to Face.
    # Let's try to mock a result or find a specific date.

    # Actually, let's just inspect the synthesis logic with a mocked report structure
    # to avoid hunting for a specific celestial configuration.

    mock_report = {
        "soul_guardian": {},
        "vitality": {},
        "summary": {},
        "medical_analysis": {},
        "planets": [
            {
                "name": "MockPlanet",
                "sign": "Void",
                "longitude": 0.0,
                "dignities": {
                    "total_score": 0,
                    "domicile_ruler": "Nobody",
                    "exaltation_ruler": "Nobody",
                    "score_breakdown": {
                        "domicile": 0,
                        "exaltation": 0,
                        "triplicity": 0,
                        "term": 0,
                        "face": 0,
                    },
                },
                "solar_status": "Variable",
                "impacts": [],
            }
        ],
    }

    text = ReportSynthesizer._generate_planetary_protocols(mock_report)
    if "🦅 **Peregrine (Wanderer):**" in text:
        print("✅ SUCCESS: Peregrine label detected in synthesis.")
        print(text)
    else:
        print("❌ FAILURE: Peregrine label NOT detected.")


if __name__ == "__main__":
    asyncio.run(test_options())
