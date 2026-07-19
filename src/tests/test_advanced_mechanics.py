
from src.engine.advanced_mechanics import (AlmutenEngine, DodecatemoriaEngine,
                                           DoryphoryEngine, HermeticLotEngine,
                                           MonomoiriaEngine)
from src.engine.models import Chart, Planet, PlanetName, Sign


def create_mock_chart(is_day=True):
    # Sun at 10 Aries
    sun = Planet(name=PlanetName.SUN, longitude=10.0, altitude=1.0 if is_day else -1.0)
    # Moon at 20 Taurus
    moon = Planet(name=PlanetName.MOON, longitude=50.0)
    # Mercury at 0 Aries (Oriental, not combust)
    mercury = Planet(name=PlanetName.MERCURY, longitude=0.0)
    # Venus at 15 Gemini
    venus = Planet(name=PlanetName.VENUS, longitude=75.0)
    # Mars at 25 Cancer
    mars = Planet(name=PlanetName.MARS, longitude=115.0)
    # Jupiter at 5 Leo
    jupiter = Planet(name=PlanetName.JUPITER, longitude=125.0)
    # Saturn at 15 Virgo
    saturn = Planet(name=PlanetName.SATURN, longitude=165.0)

    planets = [sun, moon, mercury, venus, mars, jupiter, saturn]

    # Mock houses (Whole Sign for simplicity in tests unless needed otherwise)
    # Ascendant at 15 Aries
    asc = 15.0
    houses = {i: (asc + (i - 1) * 30) % 360 for i in range(1, 13)}

    return Chart(
        sun_altitude=sun.altitude,
        planets=planets,
        ascendant=asc,
        houses=houses,
        jd=2460000.5,  # Arbitrary JD
    )


def test_hermetic_lots():
    chart = create_mock_chart(is_day=True)
    lots = HermeticLotEngine.calculate_all_lots(chart)

    # Day: Fortune = Asc + Moon - Sun = 15 + 50 - 10 = 55 (Taurus)
    assert lots["Fortune"]["longitude"] == 55.0
    assert lots["Fortune"]["sign"] == "Taurus"

    # Day: Spirit = Asc + Sun - Moon = 15 + 10 - 50 = -25 = 335 (Pisces)
    assert lots["Spirit"]["longitude"] == 335.0
    assert lots["Spirit"]["sign"] == "Pisces"

    # Night Reversal check
    chart_night = create_mock_chart(is_day=False)
    lots_night = HermeticLotEngine.calculate_all_lots(chart_night)

    # Night: Fortune = Asc + Sun - Moon = 335
    assert lots_night["Fortune"]["longitude"] == 335.0
    # Night: Spirit = Asc + Moon - Sun = 55
    assert lots_night["Spirit"]["longitude"] == 55.0


def test_monomoiria():
    # Aries: Mars (0), Sun (1), Ven (2), Mer (3), Moon (4), Sat (5), Jup (6)
    # Domicile of Aries is Mars.
    # Degree 0-1: Mars
    assert MonomoiriaEngine.get_zoidion_monomoiria(0.5) == PlanetName.MARS
    # Degree 1-2: Sun (Chaldean Descending from Mars: Mar -> Sun -> Ven -> Mer -> Moon -> Sat -> Jup)
    assert MonomoiriaEngine.get_zoidion_monomoiria(1.5) == PlanetName.SUN

    # Trigonal
    # Light in Aries (Fire). Day: Sun.
    assert (
        MonomoiriaEngine.get_trigonal_monomoiria(0.5, True, Sign.ARIES, Sign.LEO)
        == PlanetName.SUN
    )
    # Paulus ch. 32 table is not the ordinary Chaldean sequence: degree 2
    # in the diurnal fire column is Jupiter, not Venus.
    assert (
        MonomoiriaEngine.get_trigonal_monomoiria(1.5, True, Sign.ARIES, Sign.LEO)
        == PlanetName.JUPITER
    )
    assert (
        MonomoiriaEngine.get_trigonal_monomoiria(1.5, False, Sign.ARIES, Sign.LEO)
        == PlanetName.SUN
    )
    assert (
        MonomoiriaEngine.get_trigonal_monomoiria(0.5, True, Sign.TAURUS, Sign.VIRGO)
        == PlanetName.VENUS
    )
    assert (
        MonomoiriaEngine.get_trigonal_monomoiria(3.5, False, Sign.GEMINI, Sign.AQUARIUS)
        == PlanetName.JUPITER
    )
    assert (
        MonomoiriaEngine.get_trigonal_monomoiria(6.5, False, Sign.CANCER, Sign.PISCES)
        == PlanetName.SATURN
    )


def test_almuten_scoring():
    chart = create_mock_chart(is_day=True)
    # Mocking day/hour lords
    result = AlmutenEngine.calculate_almuten(
        chart, day_lord=PlanetName.SUN, hour_lord=PlanetName.VENUS
    )

    assert result.winner in [p for p in PlanetName]
    assert len(result.scores) == 7


def test_doryphory():
    chart = create_mock_chart(is_day=True)
    # Sun at 10, Mercury at 5. Mercury is Oriental (Preceding).
    guards = DoryphoryEngine.check_doryphory(chart)

    merc_guard = next(
        (
            g
            for g in guards
            if g.planet == PlanetName.MERCURY and g.related_luminary == "Sun"
        ),
        None,
    )
    assert merc_guard is not None
    assert merc_guard.phase == "oriental"
    assert merc_guard.placement_relation == "same_sign"


def test_doryphory_uses_next_following_sign_not_fixed_thirty_degrees():
    chart = create_mock_chart(is_day=True)
    sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
    moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
    mercury = next(p for p in chart.planets if p.name == PlanetName.MERCURY)
    sun.longitude = 141.096609  # Leo 21
    moon.longitude = 133.246366  # Leo 13
    mercury.longitude = 167.182642  # Virgo 17; 33.94 degrees after Moon

    guards = DoryphoryEngine.check_doryphory(chart)

    lunar_mercury = next(
        guard
        for guard in guards
        if guard.planet == PlanetName.MERCURY
        and guard.related_luminary == "Moon"
    )
    assert lunar_mercury.phase == "occidental"
    assert lunar_mercury.placement_relation == "next_following_sign"
    assert not any(
        guard.planet == PlanetName.MERCURY
        and guard.related_luminary == "Sun"
        for guard in guards
    )


def test_doryphory_excludes_outer_planets_and_wrong_phase():
    chart = create_mock_chart(is_day=True)
    chart.planets.append(
        Planet(name=PlanetName.URANUS, longitude=5.0)
    )
    # Venus is in the sign following the Moon but is oriental, so it cannot
    # serve the Moon under Ptolemy's vespertine/occidental condition.
    sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
    moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
    venus = next(p for p in chart.planets if p.name == PlanetName.VENUS)
    sun.longitude = 100.0
    moon.longitude = 50.0
    venus.longitude = 65.0

    guards = DoryphoryEngine.check_doryphory(chart)

    assert all(guard.planet != PlanetName.URANUS for guard in guards)
    assert not any(
        guard.planet == PlanetName.VENUS and guard.related_luminary == "Moon"
        for guard in guards
    )


def test_dodecatemoria():
    # 10 Aries. Degree-in-sign = 10.
    # Valens: sign_start(0) + 10*12 = 0 + 120 = 120.0 (0° Leo)
    lon_v = DodecatemoriaEngine.calculate_dodecatemoria_valens(10.0)
    assert lon_v == 120.0

    # Paul: sign_start(0) + 10*13 = 0 + 130 = 130.0 (10° Leo)
    lon_p = DodecatemoriaEngine.calculate_dodecatemoria_paul(10.0)
    assert lon_p == 130.0
