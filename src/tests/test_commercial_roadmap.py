import os

# Set dummy env vars for Settings validation during import
os.environ["STRIPE_SECRET_KEY"] = "sk_test_mock"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_mock"
os.environ["JWT_SECRET"] = "mock_secret"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SENDER_EMAIL"] = "mock@example.com"

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Request
from src.api.v1.middleware.rate_limiting import enforce_rate_limit
from src.database.models import User, SubscriptionPlan, UserSubscription

class MockRequest:
    def __init__(self, host="127.0.0.1"):
        self.client = MagicMock()
        self.client.host = host

@pytest.mark.asyncio
async def test_enforce_rate_limit_agency():
    # Setup
    plan = MagicMock(spec=SubscriptionPlan)
    plan.tier = 'agency'
    user = MagicMock(spec=User)
    user.id = "user123"
    auth_context = {
        "api_key_id": "key_agency",
        "user": user,
        "plan": plan
    }
    request = MockRequest()
    
    with patch('src.api.v1.middleware.rate_limiting.rate_limiter') as mock_limiter:
        mock_limiter.check_rate_limit.return_value = (True, {"limit": 1000})
        
        # Execute
        result = await enforce_rate_limit(request, auth_context)
        
        # Verify
        mock_limiter.check_rate_limit.assert_called_with("key_agency", 1000)
        assert result["limit"] == 1000

@pytest.mark.asyncio
async def test_enforce_rate_limit_free_fallback():
    # Setup
    request = MockRequest(host="192.168.1.1")
    
    with patch('src.api.v1.middleware.rate_limiting.rate_limiter') as mock_limiter:
        mock_limiter.check_rate_limit.return_value = (True, {"limit": 10})
        
        # Execute
        result = await enforce_rate_limit(request, None)
        
        # Verify
        mock_limiter.check_rate_limit.assert_called_with("ip:192.168.1.1", 10)

@pytest.mark.asyncio
async def test_enforce_rate_limit_exceeded():
    # Setup
    plan = MagicMock(spec=SubscriptionPlan)
    plan.tier = 'master'
    user = MagicMock(spec=User)
    user.id = "user456"
    auth_context = {
        "api_key_id": "key_master",
        "user": user,
        "plan": plan
    }
    request = MockRequest()
    
    with patch('src.api.v1.middleware.rate_limiting.rate_limiter') as mock_limiter:
        mock_limiter.check_rate_limit.return_value = (False, {"limit": 100, "reset_at": 30})
        
        # Execute & Verify
        with pytest.raises(HTTPException) as excinfo:
            await enforce_rate_limit(request, auth_context)
        
        assert excinfo.value.status_code == 429
        assert excinfo.value.detail["limit"] == 100
        assert excinfo.value.detail["retry_after"] == 30
