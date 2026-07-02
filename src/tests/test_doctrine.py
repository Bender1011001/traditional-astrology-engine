"""Tests for the doctrinal-disagreement layer."""
from src.engine.doctrine import DOCTRINAL_FORKS, DoctrineEngine
from src.engine.models import PlanetName, Sect


class _P:
    def __init__(self, name, lon):
        self.name = name
        self.longitude = lon


class _C:
    def __init__(self, planets):
        self.planets = planets


def test_registry_well_formed():
    assert len(DOCTRINAL_FORKS) >= 8
    for fork in DOCTRINAL_FORKS:
        assert fork["topic"]
        assert len(fork["positions"]) >= 2
        for pos in fork["positions"]:
            assert pos["authority"] and pos["position"]
        assert fork["engine_handling"]


def test_water_triplicity_fork_for_venus_by_day():
    # Venus at 10° Cancer (water). Dorothean: Venus is the water day-ruler (+3).
    # Ptolemaic: the water day-ruler is Mars, so Venus gets none -> the schemes disagree.
    chart = _C([_P(PlanetName.VENUS, 100.0)])
    forks = DoctrineEngine.chart_dignity_forks(chart, Sect.DAY)
    trip = [f for f in forks if f["planet"] == "Venus" and f["factor"] == "triplicity dignity"]
    assert trip, "expected a triplicity disagreement for Venus in Cancer by day"
    auths = " ".join(p["authority"] for p in trip[0]["positions"])
    assert "Dorothean" in auths and "Ptolemaic" in auths
    vals = [p["value"] for p in trip[0]["positions"]]
    assert "+3" in vals and "none" in vals


def test_build_shape():
    chart = _C([_P(PlanetName.VENUS, 100.0), _P(PlanetName.SUN, 140.0)])
    out = DoctrineEngine.build(chart, Sect.DAY)
    assert "known_forks" in out and "chart_specific" in out
    assert isinstance(out["chart_specific"], list)
