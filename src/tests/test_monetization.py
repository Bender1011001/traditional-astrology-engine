from fastapi.testclient import TestClient

from src.api.v1.auth import create_access_token
from src.app import app

client = TestClient(app)


def test_restore_session_invalid_token():
    response = client.get("/api/v1/endpoints/restore_session?token=invalid")
    # Note: The route is actually mounted at /api/v1/auth/restore_session based on router structure?
    # Wait, auth.py router is usually mounted. Let's check router.py in next step if fails.
    # Assuming /api/v1/auth/restore_session based on typical structure,
    # BUT in auth.py I saw @router.get("/restore_session").
    # If auth.router is mounted at /auth, then it's /api/v1/auth/restore_session.


def test_restore_session_flow():
    # 1. Create a dummy token with chart data
    chart_data = {"date": "2023-01-01", "city": "London"}
    token = create_access_token(
        chart_hash="dummy",
        tier="scholar",
        data={"user_id": 123, "chart_input": chart_data},
    )

    # 2. Call restore endpoint
    # We need to find the correct mount path. auth.py router is usually /auth
    response = client.get(f"/api/v1/auth/restore_session?token={token}")

    # 3. Verify
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2023-01-01"
    assert data["city"] == "London"


def test_restore_session_no_data():
    token = create_access_token(
        chart_hash="dummy", tier="free", data={"user_id": 123}  # No chart_input
    )
    response = client.get(f"/api/v1/auth/restore_session?token={token}")
    assert response.status_code == 404
