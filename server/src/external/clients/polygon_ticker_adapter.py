from typing import List, Dict, Optional

from src.external.clients.polygon_client import PolygonClient
from src.ports.ticker_search import TickerSearchPort


class PolygonTickerSearchAdapter(TickerSearchPort):
    """Adapter implementing ticker search via PolygonClient."""

    def __init__(self, client: Optional[PolygonClient] = None) -> None:
        self._client = client or PolygonClient()

    def search_tickers(self, query: str, limit: int = 20, active: bool = True) -> List[Dict[str, object]]:
        return self._client.search_tickers(query=query, limit=limit, active=active)


