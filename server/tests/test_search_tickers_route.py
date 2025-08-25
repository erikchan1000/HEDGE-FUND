import json

import pytest

from src.api.routes.search_tickers import search_tickers_bp, set_ticker_search_provider
from flask import Flask


class FakeTickerPort:
    def __init__(self, results):
        self._results = results

    def search_tickers(self, query: str, limit: int = 20, active: bool = True):
        return self._results


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(search_tickers_bp)
    yield app


def test_search_tickers_missing_query_returns_400(app):
    client = app.test_client()
    resp = client.get('/api/search_tickers')
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]


def test_search_tickers_uses_injected_port(app):
    results = [{"symbol": "AAPL", "name": "Apple Inc"}]
    set_ticker_search_provider(lambda: FakeTickerPort(results))

    client = app.test_client()
    resp = client.get('/api/search_tickers?query=aap')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["results"] == results


