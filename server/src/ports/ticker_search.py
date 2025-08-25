from typing import Protocol, List, Dict


class TickerSearchPort(Protocol):
    """Port for searching tickers by query.

    Adapters implementing this protocol should return a simplified list of tickers
    with common fields like symbol and name.
    """

    def search_tickers(self, query: str, limit: int = 20, active: bool = True) -> List[Dict[str, object]]:
        """Search for tickers matching the given query.

        Args:
            query: The search text (symbol prefix or company name).
            limit: Maximum number of results to return.
            active: Whether to limit to active tickers.

        Returns:
            A list of dictionaries with at least keys: 'symbol' and 'name'.
        """
        ...


