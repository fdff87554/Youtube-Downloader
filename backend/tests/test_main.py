"""Tests for the FastAPI application factory."""

import pytest

from app.main import create_app


class TestCorsConfiguration:
    def test_create_app_raises_when_origins_missing_and_debug_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
        monkeypatch.setenv("DEBUG", "false")

        with pytest.raises(RuntimeError, match="ALLOWED_ORIGINS"):
            create_app()

    def test_create_app_allows_missing_origins_when_debug_on(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
        monkeypatch.setenv("DEBUG", "true")

        app = create_app()

        assert app.title == "YouTube Downloader API"

    def test_create_app_accepts_explicit_origins(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ALLOWED_ORIGINS", "https://example.com,https://x.com")
        monkeypatch.setenv("DEBUG", "false")

        app = create_app()

        assert app.title == "YouTube Downloader API"
