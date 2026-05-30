import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from middleware.logging_middleware import LoggingMiddleware


@pytest.mark.no_db
def test_logging_middleware_logs_request(caplog):
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="dps_api"):
        response = client.get("/ping")

    assert response.status_code == 200
    assert any("GET /ping completed with 200" in rec.message for rec in caplog.records)

