from ipaddress import ip_address
from typing import Any


_FORWARDED_IP_HEADERS = (
    "x-forwarded-for",
    "x-real-ip",
    "cf-connecting-ip",
    "true-client-ip",
)


def _clean_ip_candidate(value: str) -> str:
    candidate = str(value or "").strip().strip('"').strip("'")
    if not candidate or candidate.lower() == "unknown":
        return ""

    if candidate.startswith("[") and "]" in candidate:
        return candidate[1 : candidate.index("]")]

    # IPv4 with a port, e.g. 203.0.113.10:443. Do not split IPv6 literals.
    if candidate.count(":") == 1 and "." in candidate:
        host, _port = candidate.rsplit(":", 1)
        if host:
            return host.strip()

    return candidate


def get_client_ip(request: Any) -> str:
    """
    Return the best available visitor address behind Cloud Run/Google Frontend.

    Cloud Run's ASGI client host can be an internal link-local proxy address
    such as 169.254.169.126. Rate limits and KPI logs must use forwarded
    visitor headers first, then fall back to the socket address for local tests.
    """
    headers = getattr(request, "headers", {}) or {}

    for header in _FORWARDED_IP_HEADERS:
        raw_value = headers.get(header)
        if not raw_value:
            continue

        # X-Forwarded-For is a comma-separated chain. The first non-empty entry
        # is the original client supplied by Google Frontend.
        for part in str(raw_value).split(","):
            candidate = _clean_ip_candidate(part)
            if candidate:
                return candidate

    client = getattr(request, "client", None)
    fallback = _clean_ip_candidate(getattr(client, "host", "") if client else "")
    return fallback or "unknown"


def is_rate_limitable_client_ip(client_ip: str) -> bool:
    """
    Whether an address is suitable as a per-visitor quota key.

    Link-local Cloud Run proxy addresses and localhost should not lock out the
    whole service. Unknown/invalid-but-explicit forwarded values are still useful
    as deterministic keys in tests and non-standard proxy setups.
    """
    if not client_ip or client_ip == "unknown":
        return False

    try:
        parsed = ip_address(client_ip)
    except ValueError:
        return True

    return not (parsed.is_loopback or parsed.is_link_local)
