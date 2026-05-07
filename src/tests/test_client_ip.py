from types import SimpleNamespace

from src.api.v1.client_ip import get_client_ip, is_rate_limitable_client_ip


class MockRequest:
    def __init__(self, headers=None, host="169.254.169.126"):
        self.headers = headers or {}
        self.client = SimpleNamespace(host=host)


def test_get_client_ip_uses_first_forwarded_for_entry():
    request = MockRequest(headers={"x-forwarded-for": "198.51.100.23, 169.254.169.126"})

    assert get_client_ip(request) == "198.51.100.23"


def test_get_client_ip_strips_ipv4_port():
    request = MockRequest(headers={"x-forwarded-for": "203.0.113.8:443"})

    assert get_client_ip(request) == "203.0.113.8"


def test_cloud_run_link_local_fallback_is_not_rate_limitable():
    client_ip = get_client_ip(MockRequest(host="169.254.169.126"))

    assert client_ip == "169.254.169.126"
    assert is_rate_limitable_client_ip(client_ip) is False


def test_explicit_nonstandard_forwarded_value_is_still_a_stable_key():
    client_ip = get_client_ip(MockRequest(headers={"x-forwarded-for": "10.0.0.test"}))

    assert client_ip == "10.0.0.test"
    assert is_rate_limitable_client_ip(client_ip) is True
