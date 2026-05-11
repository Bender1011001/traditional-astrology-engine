from httpx import ASGITransport, AsyncClient
import pytest

from src.app import app
from src.engine.geomancy import cast_geomancy, combine_rows


REPORT_EXAMPLE_COUNTS = [
    8,
    12,
    6,
    7,
    10,
    4,
    9,
    14,
    2,
    6,
    11,
    5,
    16,
    3,
    8,
    12,
]


def test_geomancy_report_example_derives_judge_and_outcome():
    result = cast_geomancy(
        "Will the messenger arrive?",
        mother_counts=REPORT_EXAMPLE_COUNTS,
    )

    assert result["mothers"] == [
        [2, 2, 2, 1],
        [2, 2, 1, 2],
        [2, 2, 1, 1],
        [2, 1, 2, 2],
    ]
    assert result["judge"]["rows"] == [1, 2, 2, 1]
    assert result["judge"]["name"] == "Carcer"
    assert result["outcome"]["rows"] == [1, 2, 2, 2]
    assert result["outcome"]["name"] == "Laetitia"
    assert result["validity"]["valid"] is True
    assert result["validity"]["judge_total_points"] == 6
    assert result["shield"][12]["role"] == "W1"
    assert result["shield"][12]["house_english"] == "questioner"
    assert result["shield"][13]["role"] == "W2"
    assert result["shield"][13]["house_english"] == "asked-about party"
    assert "Historical Use Only" in result["safety_notice"]
    assert "deep-research-report.md" in result["source_basis"]["procedural_source"]


def test_geomancy_combination_uses_odd_even_parity_rule():
    assert combine_rows((1, 1, 2, 1), (2, 1, 2, 2)) == (1, 2, 2, 1)


@pytest.mark.asyncio
async def test_geomancy_api_accepts_report_line_counts():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://traditional-astrology.test"
    ) as ac:
        response = await ac.post(
            "/api/v1/geomancy/cast",
            json={
                "question": "Will the messenger arrive?",
                "mother_counts": REPORT_EXAMPLE_COUNTS,
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["generation_method"] == "user_line_counts"
    assert data["judge"]["rows"] == [1, 2, 2, 1]
    assert data["outcome"]["rows"] == [1, 2, 2, 2]
    assert data["judgement"]["verdict"] in {
        "FAVORABLE",
        "LEANING FAVORABLE",
        "MIXED",
        "LEANING UNFAVORABLE",
        "UNFAVORABLE",
    }


@pytest.mark.asyncio
async def test_geomancy_api_generates_secure_counts_when_none_supplied():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://traditional-astrology.test"
    ) as ac:
        response = await ac.post(
            "/api/v1/geomancy/cast",
            json={"question": "Will the matter resolve?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["generation_method"] == "server_secure_random_counts"
    assert len(data["raw_counts"]) == 16
    assert len(data["shield"]) == 16
    assert data["validity"]["valid"] is True
