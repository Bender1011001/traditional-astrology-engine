from fastapi.testclient import TestClient

from src.app import app
from src.database.core import Base, engine

# Note: the app fixture might already be using the test db,
# but we can enforce tables are created just in case
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_horary_api_requires_subscription_authentication():
    response = client.post(
        "/api/v1/horary",
        json={"question": "Will this require access?", "city": "London", "state": "UK"},
    )
    assert response.status_code == 401
    assert "Account sign-in is required" in response.json()["detail"]
