import pytest

from src.external.clients.polygon_ticker_adapter import PolygonTickerSearchAdapter


class DummyPolygonClient:
    def __init__(self, results):
        self._results = results

    def search_tickers(self, query: str, limit: int = 20, active: bool = True):
        return [r for r in self._results if query.lower() in (r.get('symbol','') + r.get('name','')).lower()][:limit]


def test_polygon_adapter_returns_results_passthrough():
    results = [
        {"symbol": "AAPL", "name": "Apple Inc"},
        {"symbol": "MSFT", "name": "Microsoft Corp"},
    ]
    adapter = PolygonTickerSearchAdapter(client=DummyPolygonClient(results))

    out = adapter.search_tickers("AAP")

    assert isinstance(out, list)
    assert out and out[0]["symbol"] == "AAPL"


def test_polygon_adapter_limit_and_active_params_forwarded():
    class SpyClient(DummyPolygonClient):
        def __init__(self, results):
            super().__init__(results)
            self.calls = []

        def search_tickers(self, query: str, limit: int = 20, active: bool = True):
            self.calls.append({"query": query, "limit": limit, "active": active})
            return super().search_tickers(query, limit=limit, active=active)

    spy = SpyClient([
        {"symbol": "AAPL", "name": "Apple Inc"},
        {"symbol": "MSFT", "name": "Microsoft Corp"},
    ])
    adapter = PolygonTickerSearchAdapter(client=spy)

    adapter.search_tickers("A", limit=1, active=False)

    assert spy.calls[-1] == {"query": "A", "limit": 1, "active": False}


