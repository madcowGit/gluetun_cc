"""Tests for the Gluetun integration's URL handling and HTTP client."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.gluetun_cc import _entry_settings
from custom_components.gluetun_cc import config_flow, coordinator
from custom_components.gluetun_cc.const import (
    CONF_INSTANCE_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_INSTANCE_NAME,
    VPN_STATUS_ENDPOINT,
)


def _response_context(status: int, *, text: str = "", json_data=None):
    """Build an aiohttp-style async response context manager."""
    response = MagicMock()
    response.status = status
    response.text = AsyncMock(return_value=text)
    response.json = AsyncMock(return_value=json_data)

    context = AsyncMock()
    context.__aenter__.return_value = response
    return context


def test_normalize_url_strips_whitespace_and_trailing_slash():
    assert (
        config_flow._normalize_and_validate_url("  https://gluetun:8000///  ")
        == "https://gluetun:8000"
    )


@pytest.mark.parametrize(
    "url",
    [
        "gluetun:8000",
        "ftp://gluetun:8000",
        "http://",
        "http://user:password@gluetun:8000",
    ],
)
def test_normalize_url_rejects_invalid_or_credentialed_urls(url):
    with pytest.raises(vol.Invalid):
        config_flow._normalize_and_validate_url(url)


def test_entry_settings_support_legacy_config_entries():
    entry = SimpleNamespace(data={})

    assert _entry_settings(entry) == (
        DEFAULT_INSTANCE_NAME,
        DEFAULT_BASE_URL,
        "",
        "",
    )


def test_entry_settings_normalizes_saved_base_url():
    entry = SimpleNamespace(
        data={
            CONF_INSTANCE_NAME: "home-vpn",
            "base_url": "http://gluetun:8000/",
            "api_key": "secret",
            "tunnel_name": "wireguard",
        }
    )

    assert _entry_settings(entry) == (
        "home-vpn",
        "http://gluetun:8000",
        "secret",
        "wireguard",
    )


def test_validate_connection_sends_api_key(monkeypatch):
    session = MagicMock()
    session.get.return_value = _response_context(200, json_data={"status": "running"})
    monkeypatch.setattr(config_flow, "async_get_clientsession", lambda hass: session)

    result = asyncio.run(
        config_flow._validate_connection(MagicMock(), "http://gluetun", "key")
    )

    assert result is None
    args, kwargs = session.get.call_args
    assert args == (f"http://gluetun{VPN_STATUS_ENDPOINT}",)
    assert kwargs["headers"] == {
        "Accept": "application/json",
        "X-API-Key": "key",
    }


@pytest.mark.parametrize(
    ("status", "json_data", "expected"),
    [
        (401, None, "invalid_auth"),
        (503, None, "cannot_connect"),
        (200, ["unexpected", "array"], "invalid_response"),
    ],
)
def test_validate_connection_reports_server_errors(monkeypatch, status, json_data, expected):
    session = MagicMock()
    session.get.return_value = _response_context(status, json_data=json_data)
    monkeypatch.setattr(config_flow, "async_get_clientsession", lambda hass: session)

    assert (
        asyncio.run(
            config_flow._validate_connection(MagicMock(), "http://gluetun", "")
        )
        == expected
    )


def test_api_get_json_returns_object_and_uses_auth_header(monkeypatch):
    session = MagicMock()
    session.get.return_value = _response_context(200, text='{"status":"running"}')
    monkeypatch.setattr(coordinator, "async_get_clientsession", lambda hass: session)
    api = coordinator.GluetunApi(MagicMock(), "http://gluetun/", "secret")

    result = asyncio.run(api.get_json(VPN_STATUS_ENDPOINT))

    assert result == {"status": "running"}
    args, kwargs = session.get.call_args
    assert args == (f"http://gluetun{VPN_STATUS_ENDPOINT}",)
    assert kwargs["headers"] == {
        "Accept": "application/json",
        "X-API-Key": "secret",
    }


def test_api_get_json_rejects_non_object_response(monkeypatch):
    session = MagicMock()
    session.get.return_value = _response_context(200, text='["not", "an object"]')
    monkeypatch.setattr(coordinator, "async_get_clientsession", lambda hass: session)
    api = coordinator.GluetunApi(MagicMock(), "http://gluetun", "")

    with pytest.raises(UpdateFailed):
        asyncio.run(api.get_json(VPN_STATUS_ENDPOINT))


def test_api_set_vpn_status_sends_put_request(monkeypatch):
    session = MagicMock()
    session.put.return_value = _response_context(204)
    monkeypatch.setattr(coordinator, "async_get_clientsession", lambda hass: session)
    api = coordinator.GluetunApi(MagicMock(), "http://gluetun", "secret")

    asyncio.run(api.set_vpn_status("running"))

    args, kwargs = session.put.call_args
    assert args == (f"http://gluetun{VPN_STATUS_ENDPOINT}",)
    assert kwargs["json"] == {"status": "running"}
    assert kwargs["headers"]["X-API-Key"] == "secret"


def test_api_set_vpn_status_raises_for_failed_request(monkeypatch):
    session = MagicMock()
    session.put.return_value = _response_context(403)
    monkeypatch.setattr(coordinator, "async_get_clientsession", lambda hass: session)
    api = coordinator.GluetunApi(MagicMock(), "http://gluetun", "secret")

    with pytest.raises(HomeAssistantError):
        asyncio.run(api.set_vpn_status("stopped"))
