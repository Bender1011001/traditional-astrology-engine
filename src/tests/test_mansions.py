"""Tests for mansions.py — 28 Lunar Mansions (Picatrix)."""
from src.engine.mansions import LunarMansionEngine


# ─── Catalog completeness ────────────────────────────────────────────────────

def test_mansions_count():
    assert len(LunarMansionEngine.MANSIONS) == 28


def test_mansions_have_required_keys():
    for m in LunarMansionEngine.MANSIONS:
        assert "mansion_id" in m
        assert "name" in m
        assert "start_lon_deg" in m
        assert "end_lon_deg" in m
        assert "intents_good" in m
        assert "intents_bad" in m
        assert "source_refs" in m


def test_mansions_ids_sequential():
    for i, m in enumerate(LunarMansionEngine.MANSIONS):
        assert m["mansion_id"] == i + 1, f"Mansion {i}: expected id={i+1}, got {m['mansion_id']}"


def test_mansions_cover_360():
    """All mansions should seamlessly cover 0°—360°."""
    assert LunarMansionEngine.MANSIONS[0]["start_lon_deg"] == 0.0
    assert abs(LunarMansionEngine.MANSIONS[-1]["end_lon_deg"] - 360.0) < 0.01


def test_mansion_boundaries_contiguous():
    """Each mansion's end should be the next mansion's start."""
    for i in range(27):
        end = LunarMansionEngine.MANSIONS[i]["end_lon_deg"]
        start_next = LunarMansionEngine.MANSIONS[i + 1]["start_lon_deg"]
        assert abs(end - start_next) < 0.001, f"Gap between mansion {i+1} and {i+2}: end={end}, start={start_next}"


def test_mansion_width():
    """Each mansion should be ~12.857° wide."""
    for m in LunarMansionEngine.MANSIONS:
        width = m["end_lon_deg"] - m["start_lon_deg"]
        assert abs(width - LunarMansionEngine.MANSION_WIDTH) < 0.01, f"{m['name']} width: {width}"


def test_all_mansions_have_sources():
    """Every mansion should cite at least one source."""
    for m in LunarMansionEngine.MANSIONS:
        assert len(m["source_refs"]) >= 1, f"{m['name']} has no source refs"


# ─── get_lunar_mansion ───────────────────────────────────────────────────────

def test_mansion_first():
    """0° should be Al-Sharatain (mansion 1)."""
    result = LunarMansionEngine.get_lunar_mansion(0.0)
    assert result["mansion_id"] == 1
    assert result["name"] == "Al-Sharatain"


def test_mansion_last():
    """359° should be Batn al-Hut (mansion 28)."""
    result = LunarMansionEngine.get_lunar_mansion(359.0)
    assert result["mansion_id"] == 28
    assert result["name"] == "Batn al-Hut"


def test_mansion_middle():
    """90° should be mansion 8 (Al-Nathrah)."""
    result = LunarMansionEngine.get_lunar_mansion(90.0)
    assert result["mansion_id"] == 8


def test_mansion_aldebaran():
    """~40° should map to mansion 4 (Aldebaran)."""
    result = LunarMansionEngine.get_lunar_mansion(40.0)
    assert result["mansion_id"] == 4
    assert result["name"] == "Aldebaran"


def test_mansion_wrap_360():
    """360° should wrap to mansion 1."""
    result = LunarMansionEngine.get_lunar_mansion(360.0)
    assert result["mansion_id"] == 1


def test_mansion_negative_wrap():
    """Negative longitude wraps correctly."""
    result = LunarMansionEngine.get_lunar_mansion(-10.0)
    assert result["mansion_id"] == 28  # 350° = mansion 28


def test_mansion_all_longitudes_valid():
    """Every degree from 0-359 should return a valid mansion."""
    for lon in range(360):
        result = LunarMansionEngine.get_lunar_mansion(float(lon))
        assert 1 <= result["mansion_id"] <= 28


def test_mansion_has_intents():
    """Every result should have good and bad intents."""
    result = LunarMansionEngine.get_lunar_mansion(100.0)
    assert isinstance(result["intents_good"], list)
    assert isinstance(result["intents_bad"], list)
    assert len(result["intents_good"]) > 0


def test_mansion_width_constant():
    assert abs(LunarMansionEngine.MANSION_WIDTH - 360.0 / 28) < 0.0001
