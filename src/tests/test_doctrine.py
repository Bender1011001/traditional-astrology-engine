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


def test_water_triplicity_ptolemy_and_dorotheus_agree_venus_by_day():
    """Venus at 10 Cancer by day: Dorotheus and Ptolemy BOTH give her the trigon.

    This test previously asserted the opposite - that the two schemes disagree,
    because the engine's "Ptolemaic" water row read Mars by day. That row was a
    blend of two traditions: Ptolemy gives Venus by day (Tetrabiblos, trigons
    chapter), Lilly gives Mars by day and night, and the table held Mars-by-day
    with Moon-by-night, which is neither. With the traditions separated, the
    genuine disagreement here is Ptolemy vs Lilly, not Dorotheus vs Ptolemy.
    """
    chart = _C([_P(PlanetName.VENUS, 100.0)])
    forks = DoctrineEngine.chart_dignity_forks(chart, Sect.DAY)
    trip = [f for f in forks if f["planet"] == "Venus" and f["factor"] == "triplicity dignity"]
    assert not trip, (
        "Dorotheus and Ptolemy both make Venus the watery day-ruler, so there is "
        "no triplicity fork for her here"
    )


def test_ptolemaic_and_lilly_triplicity_tables_are_separate_traditions():
    """The two must not be blended, and their water rows must differ."""
    from src.engine.reference_data import LILLY_TRIPLICITY, PTOLEMAIC_TRIPLICITY

    # Ptolemy: Venus by day, Moon by night. Lilly: Mars by day and night.
    assert PTOLEMAIC_TRIPLICITY["Water"] == (PlanetName.VENUS, PlanetName.MOON)
    assert LILLY_TRIPLICITY["Water"] == (PlanetName.MARS, PlanetName.MARS)
    assert PTOLEMAIC_TRIPLICITY["Water"] != LILLY_TRIPLICITY["Water"]
    # They agree everywhere else; water is the whole of the disagreement.
    for element in ("Fire", "Earth", "Air"):
        assert PTOLEMAIC_TRIPLICITY[element] == LILLY_TRIPLICITY[element]
    # And the old hybrid must never come back.
    assert PTOLEMAIC_TRIPLICITY["Water"] != (PlanetName.MARS, PlanetName.MOON)


def test_build_shape():
    chart = _C([_P(PlanetName.VENUS, 100.0), _P(PlanetName.SUN, 140.0)])
    out = DoctrineEngine.build(chart, Sect.DAY)
    assert "known_forks" in out and "chart_specific" in out
    assert isinstance(out["chart_specific"], list)
