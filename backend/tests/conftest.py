"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Create a test client for the FastAPI application.

    Sets DEBUG=true so the CORS configuration accepts a missing
    ALLOWED_ORIGINS without raising during create_app().
    """
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    app = create_app()
    return TestClient(app)
