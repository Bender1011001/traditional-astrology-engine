from fastapi.testclient import TestClient

from src.app import app
from src.database.core import Base, engine

# Note: the app fixture might already be using the test db,
# but we can enforce tables are created just in case
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_horary_rate_limit():
    import uuid

    mock_ip = (
        f"10.0.0.{uuid.uuid4().hex[:6]}"  # Guaranteed unique mock IP for test isolation
    )
    # Make 5 valid requests
    for i in range(5):
        response = client.post(
            "/api/v1/horary",
            headers={"X-Forwarded-For": mock_ip},
            json={"question": f"Test Question {i}", "city": "London", "state": "UK"},
        )
        assert response.status_code == 200, f"Request {i+1} failed"
        assert "oracle" in response.json()

    # The 6th request must be blocked
    blocked_response = client.post(
        "/api/v1/horary",
        headers={"X-Forwarded-For": mock_ip},
        json={"question": "The 6th Question", "city": "London", "state": "UK"},
    )
    assert blocked_response.status_code == 429
    assert "limit of 5 Horary questions exceeded" in blocked_response.json()["detail"]
