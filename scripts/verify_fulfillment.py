import asyncio
import sys
import os
import logging

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO)

from src.services.fulfillment import FulfillmentService

async def test_fulfillment():
    print("=== Testing Fulfillment Service ===")
    
    # Mock Data
    mock_email = "test_user@example.com"
    mock_name = "Test User"
    mock_chart_request = {
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "",
        "name": "Test Native"
    }
    
    print(f"Target: {mock_email}")
    print(f"Data: {mock_chart_request}")
    
    try:
        await FulfillmentService.fulfill_order(
            user_email=mock_email,
            user_name=mock_name,
            chart_request=mock_chart_request,
            tier="full" # Request full report to stress test
        )
        print("\n✅ Verification Successful: FulfillmentService completed without error.")
        print("(Check logs above for 'Sending email' confirmation)")
        
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fulfillment())
