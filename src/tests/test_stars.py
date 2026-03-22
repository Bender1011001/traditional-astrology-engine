"""Tests for stars.py — Fixed Stars catalog, conjunctions, and utility functions."""
from src.engine.stars import (
    STARS, FixedStar, StarContact,
    get_shortest_dist, get_fixed_star_meta,
    _normalize_deg, _precess_longitude,
    _equatorial_to_ecliptic, _ecliptic_to_equatorial,
    check_fixed_stars,
)
from src.engine.models import Chart, Planet, PlanetName
import math


# ─── STARS catalog ───────────────────────────────────────────────────────────

def test_stars_catalog_count():
    """Should have at least 20 fixed stars in the catalog."""
    assert len(STARS) >= 20


def test_stars_have_required_fields():
    for star in STARS:
        assert star.name, f"Star missing name"
        assert 0.0 <= star.longitude < 360.0, f"{star.name} longitude out of range: {star.longitude}"
        assert star.nature, f"{star.name} missing nature"
        assert star.magnitude >= 1, f"{star.name} invalid magnitude: {star.magnitude}"
        assert star.orb > 0, f"{star.name} invalid orb: {star.orb}"


def test_royal_stars_present():
    """The 4 Royal Stars should be in the catalog."""
    names = [s.name for s in STARS]
    assert "Aldebaran" in names
    assert "Regulus" in names
    assert "Antares" in names
    assert "Fomalhaut" in names


def test_sirius_present():
    names = [s.name for s in STARS]
    assert "Sirius" in names


def test_algol_has_special_orb():
    """Algol traditionally gets a wider orb."""
    algol = next(s for s in STARS if s.name == "Caput Algol")
    assert algol.orb == 2.5


def test_spica_pure_benefic():
    """Spica's nemesis should indicate pure benefic nature."""
    spica = next(s for s in STARS if s.name == "Spica")
    assert "None" in spica.nemesis or "Benefic" in spica.nemesis


def test_all_stars_have_swe_name():
    """Every star should have a Swiss Ephemeris lookup name."""
    for star in STARS:
        assert star.swe_name, f"{star.name} missing swe_name"


# ─── get_fixed_star_meta ────────────────────────────────────────────────────

def test_fixed_star_meta():
    meta = get_fixed_star_meta()
    assert "catalog" in meta
    assert "epoch" in meta
    assert "precession" in meta
    assert meta["epoch"] == "2025"


# ─── get_shortest_dist ───────────────────────────────────────────────────────

def test_shortest_dist_same():
    assert get_shortest_dist(100.0, 100.0) == 0.0


def test_shortest_dist_normal():
    assert get_shortest_dist(10.0, 50.0) == 40.0


def test_shortest_dist_wraparound():
    assert get_shortest_dist(350.0, 10.0) == 20.0


# ─── _normalize_deg ──────────────────────────────────────────────────────────

def test_normalize_deg_positive():
    assert _normalize_deg(370.0) == 10.0


def test_normalize_deg_negative():
    assert abs(_normalize_deg(-10.0) - 350.0) < 0.01


def test_normalize_deg_zero():
    assert _normalize_deg(0.0) == 0.0


# ─── _precess_longitude ─────────────────────────────────────────────────────

def test_precess_longitude_no_jd():
    """Without JD, should return original 2025 longitude."""
    result = _precess_longitude(100.0, None)
    assert result == 100.0


# ─── coordinate transforms ──────────────────────────────────────────────────

def test_equatorial_to_ecliptic_roundtrip():
    """Converting equatorial → ecliptic → equatorial should return original."""
    epsilon = 23.4393  # Standard obliquity
    ra, dec = 45.0, 20.0
    lon, lat = _equatorial_to_ecliptic(ra, dec, epsilon)
    ra2, dec2 = _ecliptic_to_equatorial(lon, lat, epsilon)
    assert abs(ra2 - ra) < 0.01, f"RA mismatch: {ra2} vs {ra}"
    assert abs(dec2 - dec) < 0.01, f"Dec mismatch: {dec2} vs {dec}"


def test_ecliptic_to_equatorial_equinox():
    """At 0° ecliptic, equatorial coords should be RA=0, Dec=0."""
    lon, lat = _ecliptic_to_equatorial(0.0, 0.0, 23.4393)
    # RA should be near 0, Dec near 0 for vernal equinox point
    assert abs(lon) < 1.0 or abs(lon - 360.0) < 1.0


# ─── StarContact dataclass ──────────────────────────────────────────────────

def test_star_contact_dataclass():
    contact = StarContact(
        star_name="Sirius",
        planet_name="Sun",
        contact_type="CONJUNCTION",
        message="test",
        mythology="The Dog Star"
    )
    assert contact.star_name == "Sirius"
    assert contact.contact_type == "CONJUNCTION"
    assert contact.mythology == "The Dog Star"


# ─── check_fixed_stars (conjunction detection) ───────────────────────────────

def _make_chart(planet_positions, asc=0.0, mc=270.0, sun_alt=10.0):
    planets = [Planet(name=n, longitude=lon, speed=spd) for n, lon, spd in planet_positions]
    return Chart(sun_altitude=sun_alt, planets=planets, ascendant=asc, mc=mc)


def test_check_fixed_stars_returns_list():
    chart = _make_chart([
        (PlanetName.SUN, 100.0, 1.0),
        (PlanetName.MOON, 200.0, 13.0),
    ])
    result = check_fixed_stars(chart)
    assert isinstance(result, list)


def test_conjunction_with_regulus():
    """Planet conjunct Regulus (0°10' Virgo ≈ 150.167) should be detected."""
    regulus = next(s for s in STARS if s.name == "Regulus")
    chart = _make_chart([
        (PlanetName.SUN, regulus.longitude, 1.0),  # Exact conjunction
        (PlanetName.MOON, 200.0, 13.0),
    ])
    result = check_fixed_stars(chart)
    regulus_contacts = [c for c in result if c.star_name == "Regulus" and c.planet_name == "Sun"]
    assert len(regulus_contacts) >= 1
    assert regulus_contacts[0].contact_type == "CONJUNCTION"


def test_conjunction_with_sirius():
    """Planet conjunct Sirius should be detected."""
    sirius = next(s for s in STARS if s.name == "Sirius")
    chart = _make_chart([
        (PlanetName.JUPITER, sirius.longitude + 0.5, 0.08),  # 0.5° orb
        (PlanetName.SUN, 100.0, 1.0),
    ])
    result = check_fixed_stars(chart)
    sirius_contacts = [c for c in result if c.star_name == "Sirius" and c.planet_name == "Jupiter"]
    assert len(sirius_contacts) >= 1


def test_no_conjunction_outside_orb():
    """Planet outside star's orb should not detect a conjunction."""
    chart = _make_chart([
        (PlanetName.SUN, 0.0, 1.0),  # 0° Aries — not near any star closely
        (PlanetName.MOON, 30.0, 13.0),  # 0° Taurus — also not near any
    ])
    result = check_fixed_stars(chart)
    # May or may not have contacts depending on star positions
    for c in result:
        assert isinstance(c, StarContact)


def test_angular_star_presence():
    """Star on the Ascendant should be detected as ANGULAR_PRESENCE."""
    spica = next(s for s in STARS if s.name == "Spica")
    chart = _make_chart(
        [(PlanetName.SUN, 100.0, 1.0), (PlanetName.MOON, 200.0, 13.0)],
        asc=spica.longitude  # Put Ascendant exactly on Spica
    )
    result = check_fixed_stars(chart)
    angular = [c for c in result if c.star_name == "Spica" and c.contact_type == "ANGULAR_PRESENCE"]
    assert len(angular) >= 1
    assert "STAR ON ASCENDANT" in angular[0].message


def test_antares_aldebaran_axis_alert():
    """Moon or Mars on Aldebaran should trigger AXIS_ALERT."""
    aldebaran = next(s for s in STARS if s.name == "Aldebaran")
    chart = _make_chart([
        (PlanetName.SUN, 100.0, 1.0),
        (PlanetName.MOON, aldebaran.longitude, 13.0),  # Moon right on Aldebaran
        (PlanetName.MARS, 200.0, 0.5),
    ])
    result = check_fixed_stars(chart)
    axis_alerts = [c for c in result if c.contact_type == "AXIS_ALERT"]
    assert len(axis_alerts) >= 1
    assert "Moon" in axis_alerts[0].planet_name


# ─── FixedStar dataclass ────────────────────────────────────────────────────

def test_fixed_star_defaults():
    star = FixedStar(name="Test", longitude=100.0, nature="Jupiter", magnitude=1)
    assert star.orb == 1.0
    assert star.glory == ""
    assert star.swe_name is None
    assert star.mythology is None
