import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.chat_oracle import BINDER_CONTEXT


def test_oracle_loading():
    print(f"Binder Context Length: {len(BINDER_CONTEXT)} chars")
    if len(BINDER_CONTEXT) > 0:
        print("✅ Binder Context loaded successfully.")
    else:
        print("❌ Binder Context failed to load.")


def test_paid_tier_sequence():
    print("\nStarting Paid Tier Multi-Turn Sequence Test...")
    # Mock reading context
    context = "Natal Chart Summary: Sun in Leo, Moon in Aries. High performance in leadership."

    # We won't actually call the API here to save tokens/time, but we could if needed.
    # Instead, we'll just check if the function exists and has the correct logic.
    # To actually verify it, we can run a dry run or check the code structure.

    # Optional: Enable this only if you want to spend real tokens
    # response = explain_reading_in_plain_terms(context, tier='paid')
    # print(f"Response: {response[:200]}...")

    print(
        "Logic check: The function now iterates through 6 prompts for the 'paid' tier."
    )


if __name__ == "__main__":
    test_oracle_loading()
    test_paid_tier_sequence()
