"""Internal Etsy shop setup tool for Traditional Astrology.

This script uses Etsy Open API v3 directly. It does not simulate Etsy writes:
commands that create or update resources require real Etsy API credentials and
return Etsy's actual response payloads.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOKEN_FILE = ROOT / ".credentials" / "etsy_tokens.json"
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_SCOPES = "shops_r shops_w listings_r listings_w"
OPEN_API_BASE_URL = os.getenv("ETSY_OPEN_API_BASE_URL", "https://openapi.etsy.com")
OAUTH_TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
OAUTH_AUTHORIZE_URL = "https://www.etsy.com/oauth/connect"

LISTING_FORM_FIELDS = {
    "quantity",
    "title",
    "description",
    "price",
    "who_made",
    "when_made",
    "taxonomy_id",
    "shipping_profile_id",
    "return_policy_id",
    "materials",
    "shop_section_id",
    "processing_min",
    "processing_max",
    "readiness_state_id",
    "tags",
    "styles",
    "item_weight",
    "item_length",
    "item_width",
    "item_height",
    "item_weight_unit",
    "item_dimensions_unit",
    "production_partner_ids",
    "image_ids",
    "is_supply",
    "is_customizable",
    "should_auto_renew",
    "is_taxable",
    "type",
}

SHOP_FORM_FIELDS = {
    "title",
    "announcement",
    "sale_message",
    "digital_sale_message",
    "policy_additional",
}

TITLE_SINGLE_USE_CHARS = ("%", ":", "&", "+")


class EtsySetupError(Exception):
    """Raised for local validation and configuration failures."""


class EtsyApiError(Exception):
    """Raised when Etsy returns a non-success HTTP response."""

    def __init__(self, message: str, status_code: int, response_body: Any) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


@dataclass(frozen=True)
class TokenBundle:
    access_token: str | None
    refresh_token: str | None


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise EtsySetupError(f"JSON file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EtsySetupError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EtsySetupError(f"Expected top-level JSON object in {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _redact(value: str | None) -> str | None:
    if not value:
        return value
    if len(value) <= 10:
        return "***"
    return f"{value[:5]}...{value[-4:]}"


def _truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _api_key_header() -> str:
    key = os.getenv("ETSY_API_KEY")
    secret = os.getenv("ETSY_SHARED_SECRET")
    missing = [name for name, value in (("ETSY_API_KEY", key), ("ETSY_SHARED_SECRET", secret)) if not value]
    if missing:
        raise EtsySetupError(f"Missing required Etsy API credential(s): {', '.join(missing)}")
    return f"{key}:{secret}"


def _load_token_bundle(token_file: Path) -> TokenBundle:
    env_access = os.getenv("ETSY_ACCESS_TOKEN")
    env_refresh = os.getenv("ETSY_REFRESH_TOKEN")
    file_access = None
    file_refresh = None
    if token_file.exists():
        data = _load_json(token_file)
        file_access = data.get("access_token")
        file_refresh = data.get("refresh_token")
    return TokenBundle(
        access_token=env_access or file_access,
        refresh_token=env_refresh or file_refresh,
    )


def _require_access_token(token_file: Path) -> str:
    token = _load_token_bundle(token_file).access_token
    if not token:
        raise EtsySetupError(
            "Missing Etsy OAuth access token. Set ETSY_ACCESS_TOKEN or create "
            f"{token_file} with the exchange-code or refresh-token command."
        )
    return token


def _shop_id(args: argparse.Namespace) -> int:
    raw = getattr(args, "shop_id", None) or os.getenv("ETSY_SHOP_ID")
    if not raw:
        raise EtsySetupError("Missing shop ID. Pass --shop-id or set ETSY_SHOP_ID.")
    try:
        value = int(raw)
    except ValueError as exc:
        raise EtsySetupError(f"Shop ID must be numeric: {raw}") from exc
    if value <= 0:
        raise EtsySetupError("Shop ID must be a positive integer.")
    return value


def _resolve_path(raw_path: str | Path) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT / path
    return path


def _encode_form_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return str(value)


def _form_data(payload: dict[str, Any], allowed_fields: set[str]) -> list[tuple[str, str]]:
    form: list[tuple[str, str]] = []
    for key, value in payload.items():
        if key not in allowed_fields or value is None:
            continue
        if isinstance(value, list):
            if not value:
                continue
            form.append((key, ",".join(_encode_form_value(item) for item in value)))
        else:
            form.append((key, _encode_form_value(value)))
    return form


def _validate_title(title: str) -> None:
    if len(title) > 140:
        raise EtsySetupError("Etsy listing title must be 140 characters or fewer.")
    for char in TITLE_SINGLE_USE_CHARS:
        if title.count(char) > 1:
            raise EtsySetupError(f"Etsy listing title can only use '{char}' once.")


def _validate_tags(tags: Any) -> None:
    if tags is None:
        return
    if not isinstance(tags, list):
        raise EtsySetupError("Listing tags must be a JSON array.")
    if len(tags) > 13:
        raise EtsySetupError("Etsy listings can have at most 13 tags.")
    long_tags = [tag for tag in tags if len(str(tag)) > 20]
    if long_tags:
        raise EtsySetupError(f"Etsy tags must be 20 characters or fewer: {long_tags}")


def _validate_listing_payload(payload: dict[str, Any]) -> None:
    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        raise EtsySetupError("Listing payload must include a non-empty title.")
    _validate_title(title)
    _validate_tags(payload.get("tags"))
    required = ["quantity", "description", "price", "who_made", "when_made"]
    missing = [field for field in required if payload.get(field) in (None, "")]
    if missing:
        raise EtsySetupError(f"Listing payload missing required field(s): {', '.join(missing)}")
    has_taxonomy = payload.get("taxonomy_id") not in (None, "")
    has_taxonomy_query = payload.get("taxonomy_query") not in (None, "")
    if not has_taxonomy and not has_taxonomy_query:
        raise EtsySetupError("Listing payload needs taxonomy_id or taxonomy_query.")
    if payload.get("type") == "physical" and not payload.get("shipping_profile_id"):
        raise EtsySetupError("Physical listings require shipping_profile_id.")


def _flatten_taxonomy(nodes: list[dict[str, Any]], ancestors: tuple[str, ...] = ()) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for node in nodes:
        name = str(node.get("name", ""))
        path = ancestors + (name,)
        flattened.append(
            {
                "id": node.get("id"),
                "name": name,
                "level": node.get("level"),
                "path": " > ".join(path),
            }
        )
        children = node.get("children")
        if isinstance(children, list):
            flattened.extend(_flatten_taxonomy(children, path))
    return flattened


def _score_taxonomy(candidate: dict[str, Any], query_words: list[str]) -> int:
    text = f"{candidate.get('name', '')} {candidate.get('path', '')}".lower()
    score = sum(3 for word in query_words if word in str(candidate.get("name", "")).lower())
    score += sum(1 for word in query_words if word in text)
    if "digital" in text:
        score += 1
    return score


class EtsyClient:
    def __init__(self, token_file: Path, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        self.token_file = token_file
        self.timeout_seconds = timeout_seconds

    def _headers(self, oauth: bool) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "traditional-astrology-etsy-setup/1.0",
            "x-api-key": _api_key_header(),
        }
        if oauth:
            headers["Authorization"] = f"Bearer {_require_access_token(self.token_file)}"
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        oauth: bool,
        params: dict[str, Any] | None = None,
        data: list[tuple[str, str]] | dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{OPEN_API_BASE_URL.rstrip('/')}{path}"
        try:
            response = requests.request(
                method,
                url,
                headers=self._headers(oauth=oauth),
                params=params,
                data=data,
                json=json_body,
                files=files,
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise EtsySetupError(f"Etsy API request failed before a response was received: {exc}") from exc

        try:
            body: Any = response.json()
        except ValueError:
            body = response.text

        if response.status_code < 200 or response.status_code >= 300:
            raise EtsyApiError(
                f"Etsy API returned HTTP {response.status_code} for {method} {path}",
                response.status_code,
                body,
            )
        return body

    def get_shop_by_owner_user_id(self, user_id: int) -> Any:
        return self.request("GET", f"/v3/application/users/{user_id}/shops", oauth=False)

    def update_shop(self, shop_id: int, payload: dict[str, Any]) -> Any:
        return self.request(
            "PUT",
            f"/v3/application/shops/{shop_id}",
            oauth=True,
            data=_form_data(payload, SHOP_FORM_FIELDS),
        )

    def list_listings(self, shop_id: int, state: str | None = None) -> Any:
        params: dict[str, Any] = {"limit": 100, "includes": "Images,Personalization"}
        if state:
            params["state"] = state
        return self.request(
            "GET",
            f"/v3/application/shops/{shop_id}/listings",
            oauth=True,
            params=params,
        )

    def create_shop_section(self, shop_id: int, title: str) -> Any:
        return self.request(
            "POST",
            f"/v3/application/shops/{shop_id}/sections",
            oauth=True,
            data=[("title", title)],
        )

    def get_seller_taxonomy_nodes(self) -> Any:
        return self.request("GET", "/v3/application/seller-taxonomy/nodes", oauth=False)

    def resolve_taxonomy_id(self, query: str, rank: int = 1) -> dict[str, Any]:
        words = [part.lower() for part in query.split() if part.strip()]
        if not words:
            raise EtsySetupError("taxonomy_query cannot be empty.")
        response = self.get_seller_taxonomy_nodes()
        nodes = response.get("results")
        if not isinstance(nodes, list):
            raise EtsySetupError("Unexpected Etsy taxonomy response: missing results list.")
        candidates = _flatten_taxonomy(nodes)
        scored = [
            (candidate, _score_taxonomy(candidate, words))
            for candidate in candidates
            if _score_taxonomy(candidate, words) > 0
        ]
        scored.sort(key=lambda item: (item[1], len(str(item[0].get("path", "")))), reverse=True)
        if not scored:
            raise EtsySetupError(f"No taxonomy candidates matched query: {query}")
        if rank < 1 or rank > len(scored):
            raise EtsySetupError(f"Taxonomy rank {rank} is outside 1..{len(scored)}.")
        candidate, score = scored[rank - 1]
        return {
            "taxonomy_id": candidate["id"],
            "taxonomy_name": candidate["name"],
            "taxonomy_path": candidate["path"],
            "score": score,
        }

    def create_draft_listing(
        self,
        shop_id: int,
        payload: dict[str, Any],
        *,
        taxonomy_rank: int = 1,
        taxonomy_id_override: int | None = None,
    ) -> Any:
        listing_payload = dict(payload)
        if taxonomy_id_override is not None:
            listing_payload["taxonomy_id"] = taxonomy_id_override
        elif not listing_payload.get("taxonomy_id"):
            resolved = self.resolve_taxonomy_id(str(listing_payload["taxonomy_query"]), rank=taxonomy_rank)
            listing_payload["taxonomy_id"] = resolved["taxonomy_id"]
            print(
                "Resolved taxonomy: "
                f"{resolved['taxonomy_id']} ({resolved['taxonomy_path']})",
                file=sys.stderr,
            )
        _validate_listing_payload(listing_payload)
        return self.request(
            "POST",
            f"/v3/application/shops/{shop_id}/listings",
            oauth=True,
            data=_form_data(listing_payload, LISTING_FORM_FIELDS),
        )

    def update_listing_personalization(
        self,
        shop_id: int,
        listing_id: int,
        questions: list[dict[str, Any]],
    ) -> Any:
        if not questions:
            raise EtsySetupError("At least one personalization question is required.")
        return self.request(
            "POST",
            f"/v3/application/shops/{shop_id}/listings/{listing_id}/personalization",
            oauth=True,
            params={"supports_multiple_personalization_questions": "true"},
            json_body={"personalization_questions": questions},
        )

    def upload_listing_image(
        self,
        shop_id: int,
        listing_id: int,
        image_path: Path,
        *,
        rank: int,
        alt_text: str,
        overwrite: bool,
    ) -> Any:
        if not image_path.exists():
            raise EtsySetupError(f"Image does not exist: {image_path}")
        with image_path.open("rb") as image_handle:
            files = {"image": (image_path.name, image_handle)}
            data = {
                "rank": str(rank),
                "overwrite": "true" if overwrite else "false",
                "alt_text": alt_text,
            }
            return self.request(
                "POST",
                f"/v3/application/shops/{shop_id}/listings/{listing_id}/images",
                oauth=True,
                data=data,
                files=files,
            )

    def upload_listing_file(
        self,
        shop_id: int,
        listing_id: int,
        file_path: Path,
        *,
        rank: int,
        display_name: str | None,
    ) -> Any:
        if not file_path.exists():
            raise EtsySetupError(f"Digital file does not exist: {file_path}")
        upload_name = display_name or file_path.name
        with file_path.open("rb") as file_handle:
            files = {"file": (file_path.name, file_handle)}
            data = {"rank": str(rank), "name": upload_name}
            return self.request(
                "POST",
                f"/v3/application/shops/{shop_id}/listings/{listing_id}/files",
                oauth=True,
                data=data,
                files=files,
            )

    def activate_listing(self, shop_id: int, listing_id: int) -> Any:
        return self.request(
            "PATCH",
            f"/v3/application/shops/{shop_id}/listings/{listing_id}",
            oauth=True,
            data=[("state", "active")],
        )


def _token_file(args: argparse.Namespace) -> Path:
    return _resolve_path(getattr(args, "token_file", None) or DEFAULT_TOKEN_FILE)


def _client(args: argparse.Namespace) -> EtsyClient:
    return EtsyClient(_token_file(args), timeout_seconds=args.timeout)


def _extract_listing_id(response: Any) -> int:
    if not isinstance(response, dict):
        raise EtsySetupError("Expected Etsy listing response object.")
    raw = response.get("listing_id")
    if raw is None:
        raise EtsySetupError("Etsy response did not include listing_id.")
    return int(raw)


def _extract_section_id(response: Any) -> int:
    if not isinstance(response, dict):
        raise EtsySetupError("Expected Etsy shop section response object.")
    raw = response.get("shop_section_id")
    if raw is None:
        raise EtsySetupError("Etsy response did not include shop_section_id.")
    return int(raw)


def _oauth_headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "traditional-astrology-etsy-setup/1.0",
    }


def cmd_env_check(args: argparse.Namespace) -> int:
    token_file = _token_file(args)
    bundle = _load_token_bundle(token_file)
    status = {
        "ETSY_API_KEY": "present" if os.getenv("ETSY_API_KEY") else "missing",
        "ETSY_SHARED_SECRET": "present" if os.getenv("ETSY_SHARED_SECRET") else "missing",
        "ETSY_ACCESS_TOKEN": "present" if bundle.access_token else "missing",
        "ETSY_REFRESH_TOKEN": "present" if bundle.refresh_token else "missing",
        "ETSY_SHOP_ID": "present" if os.getenv("ETSY_SHOP_ID") else "missing",
        "ETSY_USER_ID": "present" if os.getenv("ETSY_USER_ID") else "missing",
        "token_file": str(token_file),
        "token_file_exists": token_file.exists(),
        "open_api_base_url": OPEN_API_BASE_URL,
    }
    _print_json(status)
    return 0


def cmd_oauth_url(args: argparse.Namespace) -> int:
    api_key = os.getenv("ETSY_API_KEY")
    if not api_key:
        raise EtsySetupError("Missing ETSY_API_KEY.")
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest())
    challenge_text = challenge.decode("ascii").rstrip("=")
    params = {
        "response_type": "code",
        "redirect_uri": args.redirect_uri,
        "scope": args.scopes,
        "client_id": api_key,
        "state": args.state or secrets.token_urlsafe(16),
        "code_challenge": challenge_text,
        "code_challenge_method": "S256",
    }
    _print_json(
        {
            "authorization_url": f"{OAUTH_AUTHORIZE_URL}?{urlencode(params)}",
            "code_verifier": verifier,
            "scopes": args.scopes,
            "redirect_uri": args.redirect_uri,
        }
    )
    return 0


def _request_token(form: dict[str, str]) -> dict[str, Any]:
    try:
        response = requests.post(
            OAUTH_TOKEN_URL,
            headers=_oauth_headers(),
            data=form,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise EtsySetupError(f"Etsy OAuth request failed before a response was received: {exc}") from exc
    try:
        body = response.json()
    except ValueError as exc:
        raise EtsySetupError(f"Etsy OAuth returned non-JSON response: {response.text}") from exc
    if response.status_code < 200 or response.status_code >= 300:
        raise EtsyApiError("Etsy OAuth token request failed", response.status_code, body)
    if not isinstance(body, dict) or not body.get("access_token"):
        raise EtsySetupError("Etsy OAuth token response did not include access_token.")
    return body


def _emit_token_response(token_file: Path, body: dict[str, Any], show_secrets: bool) -> None:
    _write_json(token_file, body)
    if show_secrets:
        _print_json({"saved_to": str(token_file), "token_response": body})
        return
    redacted = dict(body)
    redacted["access_token"] = _redact(str(redacted.get("access_token", "")))
    if redacted.get("refresh_token"):
        redacted["refresh_token"] = _redact(str(redacted["refresh_token"]))
    _print_json({"saved_to": str(token_file), "token_response": redacted})


def cmd_exchange_code(args: argparse.Namespace) -> int:
    api_key = os.getenv("ETSY_API_KEY")
    if not api_key:
        raise EtsySetupError("Missing ETSY_API_KEY.")
    body = _request_token(
        {
            "grant_type": "authorization_code",
            "client_id": api_key,
            "redirect_uri": args.redirect_uri,
            "code": args.code,
            "code_verifier": args.code_verifier,
        }
    )
    _emit_token_response(_token_file(args), body, args.show_secrets)
    return 0


def cmd_refresh_token(args: argparse.Namespace) -> int:
    api_key = os.getenv("ETSY_API_KEY")
    if not api_key:
        raise EtsySetupError("Missing ETSY_API_KEY.")
    token_file = _token_file(args)
    refresh_token = _load_token_bundle(token_file).refresh_token
    if not refresh_token:
        raise EtsySetupError("Missing Etsy refresh token.")
    body = _request_token(
        {
            "grant_type": "refresh_token",
            "client_id": api_key,
            "refresh_token": refresh_token,
        }
    )
    _emit_token_response(token_file, body, args.show_secrets)
    return 0


def cmd_shop_by_owner(args: argparse.Namespace) -> int:
    raw_user_id = args.user_id or os.getenv("ETSY_USER_ID")
    if not raw_user_id:
        raise EtsySetupError("Pass --user-id or set ETSY_USER_ID.")
    _print_json(_client(args).get_shop_by_owner_user_id(int(raw_user_id)))
    return 0


def cmd_update_shop(args: argparse.Namespace) -> int:
    payload = _load_json(_resolve_path(args.profile))
    _print_json(_client(args).update_shop(_shop_id(args), payload))
    return 0


def cmd_list_listings(args: argparse.Namespace) -> int:
    _print_json(_client(args).list_listings(_shop_id(args), state=args.state))
    return 0


def cmd_create_section(args: argparse.Namespace) -> int:
    _print_json(_client(args).create_shop_section(_shop_id(args), args.title))
    return 0


def cmd_find_taxonomy(args: argparse.Namespace) -> int:
    client = _client(args)
    response = client.get_seller_taxonomy_nodes()
    nodes = response.get("results")
    if not isinstance(nodes, list):
        raise EtsySetupError("Unexpected Etsy taxonomy response: missing results list.")
    words = [part.lower() for part in args.query.split() if part.strip()]
    candidates = _flatten_taxonomy(nodes)
    scored = [
        {
            **candidate,
            "score": _score_taxonomy(candidate, words),
        }
        for candidate in candidates
        if _score_taxonomy(candidate, words) > 0
    ]
    scored.sort(key=lambda candidate: (candidate["score"], len(str(candidate["path"]))), reverse=True)
    _print_json(scored[: args.limit])
    return 0


def cmd_create_draft(args: argparse.Namespace) -> int:
    payload = _load_json(_resolve_path(args.listing))
    response = _client(args).create_draft_listing(
        _shop_id(args),
        payload,
        taxonomy_rank=args.taxonomy_rank,
        taxonomy_id_override=args.taxonomy_id,
    )
    _print_json(response)
    return 0


def cmd_set_personalization(args: argparse.Namespace) -> int:
    payload = _load_json(_resolve_path(args.listing))
    questions = payload.get("personalization_questions")
    if not isinstance(questions, list):
        raise EtsySetupError("Listing JSON must include personalization_questions array.")
    _print_json(
        _client(args).update_listing_personalization(
            _shop_id(args),
            args.listing_id,
            questions,
        )
    )
    return 0


def cmd_upload_image(args: argparse.Namespace) -> int:
    _print_json(
        _client(args).upload_listing_image(
            _shop_id(args),
            args.listing_id,
            _resolve_path(args.image),
            rank=args.rank,
            alt_text=args.alt_text,
            overwrite=args.overwrite,
        )
    )
    return 0


def cmd_upload_file(args: argparse.Namespace) -> int:
    _print_json(
        _client(args).upload_listing_file(
            _shop_id(args),
            args.listing_id,
            _resolve_path(args.file),
            rank=args.rank,
            display_name=args.name,
        )
    )
    return 0


def cmd_activate_listing(args: argparse.Namespace) -> int:
    if not args.yes:
        raise EtsySetupError("Refusing to publish without --yes.")
    _print_json(_client(args).activate_listing(_shop_id(args), args.listing_id))
    return 0


def cmd_setup_draft(args: argparse.Namespace) -> int:
    client = _client(args)
    shop_id = _shop_id(args)
    summary: dict[str, Any] = {"shop_id": shop_id}
    if args.profile:
        summary["shop"] = client.update_shop(shop_id, _load_json(_resolve_path(args.profile)))
    section_id = args.shop_section_id
    if args.section_title:
        section_response = client.create_shop_section(shop_id, args.section_title)
        section_id = _extract_section_id(section_response)
        summary["section"] = section_response
    payload = _load_json(_resolve_path(args.listing))
    if section_id is not None:
        payload["shop_section_id"] = section_id
    listing_response = client.create_draft_listing(
        shop_id,
        payload,
        taxonomy_rank=args.taxonomy_rank,
        taxonomy_id_override=args.taxonomy_id,
    )
    listing_id = _extract_listing_id(listing_response)
    summary["listing"] = listing_response

    questions = payload.get("personalization_questions")
    if isinstance(questions, list) and questions:
        summary["personalization"] = client.update_listing_personalization(shop_id, listing_id, questions)

    if args.image:
        image_alt = args.alt_text or payload.get("image_alt_text") or payload["title"]
        summary["image"] = client.upload_listing_image(
            shop_id,
            listing_id,
            _resolve_path(args.image),
            rank=1,
            alt_text=str(image_alt),
            overwrite=True,
        )

    if args.digital_file:
        summary["file"] = client.upload_listing_file(
            shop_id,
            listing_id,
            _resolve_path(args.digital_file),
            rank=1,
            display_name=args.digital_file_name,
        )

    if args.activate:
        if not args.yes:
            raise EtsySetupError("Refusing to publish without --yes.")
        summary["activation"] = client.activate_listing(shop_id, listing_id)

    _print_json(summary)
    return 0


def _add_common_api_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--token-file", default=str(DEFAULT_TOKEN_FILE), help="Path to saved Etsy OAuth token JSON.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="HTTP timeout in seconds.")


def _add_shop_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--shop-id", type=int, help="Etsy shop ID. Defaults to ETSY_SHOP_ID.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Set up the Traditional Astrology Etsy shop with real Etsy API calls.")
    sub = parser.add_subparsers(dest="command", required=True)

    env_check = sub.add_parser("env-check", help="Show which Etsy credentials are available without printing secrets.")
    _add_common_api_args(env_check)
    env_check.set_defaults(func=cmd_env_check)

    oauth_url = sub.add_parser("oauth-url", help="Create an Etsy OAuth authorization URL with PKCE.")
    oauth_url.add_argument("--redirect-uri", required=True)
    oauth_url.add_argument("--scopes", default=DEFAULT_SCOPES)
    oauth_url.add_argument("--state")
    oauth_url.set_defaults(func=cmd_oauth_url)

    exchange_code = sub.add_parser("exchange-code", help="Exchange an OAuth code for access and refresh tokens.")
    _add_common_api_args(exchange_code)
    exchange_code.add_argument("--redirect-uri", required=True)
    exchange_code.add_argument("--code", required=True)
    exchange_code.add_argument("--code-verifier", required=True)
    exchange_code.add_argument("--show-secrets", action="store_true")
    exchange_code.set_defaults(func=cmd_exchange_code)

    refresh_token = sub.add_parser("refresh-token", help="Refresh an Etsy OAuth access token.")
    _add_common_api_args(refresh_token)
    refresh_token.add_argument("--show-secrets", action="store_true")
    refresh_token.set_defaults(func=cmd_refresh_token)

    shop_by_owner = sub.add_parser("shop-by-owner", help="Look up shop details from the Etsy owner user ID.")
    _add_common_api_args(shop_by_owner)
    shop_by_owner.add_argument("--user-id", type=int, help="Defaults to ETSY_USER_ID.")
    shop_by_owner.set_defaults(func=cmd_shop_by_owner)

    update_shop = sub.add_parser("update-shop", help="Apply shop title/announcement/sale-message fields.")
    _add_common_api_args(update_shop)
    _add_shop_arg(update_shop)
    update_shop.add_argument("--profile", default="data/etsy_shop/shop_profile.json")
    update_shop.set_defaults(func=cmd_update_shop)

    list_listings = sub.add_parser("list-listings", help="List shop listings.")
    _add_common_api_args(list_listings)
    _add_shop_arg(list_listings)
    list_listings.add_argument("--state", choices=["active", "inactive", "sold_out", "draft", "expired"])
    list_listings.set_defaults(func=cmd_list_listings)

    create_section = sub.add_parser("create-section", help="Create a shop section.")
    _add_common_api_args(create_section)
    _add_shop_arg(create_section)
    create_section.add_argument("--title", required=True)
    create_section.set_defaults(func=cmd_create_section)

    find_taxonomy = sub.add_parser("find-taxonomy", help="Search Etsy seller taxonomy candidates.")
    _add_common_api_args(find_taxonomy)
    find_taxonomy.add_argument("--query", required=True)
    find_taxonomy.add_argument("--limit", type=int, default=20)
    find_taxonomy.set_defaults(func=cmd_find_taxonomy)

    create_draft = sub.add_parser("create-draft", help="Create one draft listing from JSON.")
    _add_common_api_args(create_draft)
    _add_shop_arg(create_draft)
    create_draft.add_argument("--listing", required=True)
    create_draft.add_argument("--taxonomy-id", type=int)
    create_draft.add_argument("--taxonomy-rank", type=int, default=1)
    create_draft.set_defaults(func=cmd_create_draft)

    set_personalization = sub.add_parser("set-personalization", help="Set listing personalization questions from JSON.")
    _add_common_api_args(set_personalization)
    _add_shop_arg(set_personalization)
    set_personalization.add_argument("--listing-id", type=int, required=True)
    set_personalization.add_argument("--listing", required=True)
    set_personalization.set_defaults(func=cmd_set_personalization)

    upload_image = sub.add_parser("upload-image", help="Upload a listing image.")
    _add_common_api_args(upload_image)
    _add_shop_arg(upload_image)
    upload_image.add_argument("--listing-id", type=int, required=True)
    upload_image.add_argument("--image", required=True)
    upload_image.add_argument("--rank", type=int, default=1)
    upload_image.add_argument("--alt-text", required=True)
    upload_image.add_argument("--overwrite", action="store_true")
    upload_image.set_defaults(func=cmd_upload_image)

    upload_file = sub.add_parser("upload-file", help="Upload a digital listing file.")
    _add_common_api_args(upload_file)
    _add_shop_arg(upload_file)
    upload_file.add_argument("--listing-id", type=int, required=True)
    upload_file.add_argument("--file", required=True)
    upload_file.add_argument("--name")
    upload_file.add_argument("--rank", type=int, default=1)
    upload_file.set_defaults(func=cmd_upload_file)

    activate_listing = sub.add_parser("activate-listing", help="Publish a draft listing.")
    _add_common_api_args(activate_listing)
    _add_shop_arg(activate_listing)
    activate_listing.add_argument("--listing-id", type=int, required=True)
    activate_listing.add_argument("--yes", action="store_true")
    activate_listing.set_defaults(func=cmd_activate_listing)

    setup_draft = sub.add_parser("setup-draft", help="Apply shop profile, create a draft, set personalization, and upload assets.")
    _add_common_api_args(setup_draft)
    _add_shop_arg(setup_draft)
    setup_draft.add_argument("--profile", help="Optional shop profile JSON to apply first.")
    setup_draft.add_argument("--listing", required=True)
    setup_draft.add_argument("--section-title", help="Optional new section title to create.")
    setup_draft.add_argument("--shop-section-id", type=int)
    setup_draft.add_argument("--taxonomy-id", type=int)
    setup_draft.add_argument("--taxonomy-rank", type=int, default=1)
    setup_draft.add_argument("--image")
    setup_draft.add_argument("--alt-text")
    setup_draft.add_argument("--digital-file")
    setup_draft.add_argument("--digital-file-name")
    setup_draft.add_argument("--activate", action="store_true")
    setup_draft.add_argument("--yes", action="store_true")
    setup_draft.set_defaults(func=cmd_setup_draft)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except EtsyApiError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        _print_json({"status_code": exc.status_code, "response": exc.response_body})
        return 1
    except (EtsySetupError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
