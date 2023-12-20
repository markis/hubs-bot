import json
from typing import Any, Final

import pytest
from vcr import VCR

FILTERS: Final = [
    ("authorization", "<AUTHORIZATION>"),
    ("access_token", "<ACCESS_TOKEN>"),
    ("refresh_token", "<REFRESH_TOKEN>"),
    ("client_id", "<CLIENT_ID>"),
    ("client_secret", "<CLIENT_SECRET>"),
    ("password", "<PASSWORD>"),
    ("session_tracker", "<SESSION_TRACKER>"),
]


@pytest.fixture(autouse=True)
def vcr_config() -> dict[str, Any]:
    """Configure VCR and pytest-recording."""
    return {
        "filter_headers": [*FILTERS, "cookie"],
        "filter_post_data_parameters": FILTERS,
        "serializer": "yaml",
        "decode_compressed_response": True,
    }


def pytest_recording_configure(config: pytest.Config, vcr: VCR) -> None:
    vcr.before_record_response = scrub_response


def scrub_response(response: dict[str, Any]) -> dict[str, Any]:
    if "Set-Cookie" in response["headers"]:
        del response["headers"]["Set-Cookie"]
    if "set-cookie" in response["headers"]:
        del response["headers"]["set-cookie"]

    body = response.get("body", {}).get("string")
    if body and isinstance(body, bytes) and body.startswith(b"{") and body.endswith(b"}"):
        data = json.loads(body)
        for key, value in FILTERS:
            if key in data:
                data[key] = value

        response["body"]["string"] = json.dumps(data).encode("utf-8")
    return response
