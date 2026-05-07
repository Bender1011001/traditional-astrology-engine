from src.engine.models import Chart, Planet, PlanetName
from src.engine.synastry import SynastryEngine


def test_synastry():
    # Person A: Sun at 0 Aries, Saturn at 10 Aries
    # Person B: Sun at 0 Aries, Moon at 10 Aries
    # Fortune (Day) = Asc + Moon - Sun
    # If Asc is 0 Aries (0.0), then Fortune = 0 + 10 - 0 = 10 (Aries)

    chart_a = Chart(
        sun_altitude=10,  # Day
        planets=[
            Planet(name=PlanetName.SUN, longitude=0.0),
            Planet(name=PlanetName.SATURN, longitude=10.0),
        ],
        ascendant=0.0,
    )

    chart_b = Chart(
        sun_altitude=10,  # Day
        planets=[
            Planet(name=PlanetName.SUN, longitude=0.0),
            Planet(name=PlanetName.MOON, longitude=10.0),
        ],
        ascendant=0.0,
    )

    engine = SynastryEngine()
    analysis = engine.analyze_structural_fit(chart_a, chart_b)

    print("Synastry Analysis:")
    print(f"Overall: {analysis['overall_assessment']}")
    for audit in analysis["dependency_audits"]:
        print(f"Audit: {audit['delineation']}")
    for fate in analysis["shared_fate"]:
        print(f"Fate: {fate['delineation']}")


if __name__ == "__main__":
    test_synastry()
