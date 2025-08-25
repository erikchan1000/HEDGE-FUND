from flask import Blueprint, request, jsonify
from typing import Callable

from src.external.clients.polygon_ticker_adapter import PolygonTickerSearchAdapter
from src.ports.ticker_search import TickerSearchPort


search_tickers_bp = Blueprint('search_tickers', __name__, url_prefix='/api/search_tickers')


def _default_ticker_search_provider() -> TickerSearchPort:
    return PolygonTickerSearchAdapter()


_get_ticker_search: Callable[[], TickerSearchPort] = _default_ticker_search_provider


def set_ticker_search_provider(factory: Callable[[], TickerSearchPort]) -> None:
    global _get_ticker_search
    _get_ticker_search = factory


@search_tickers_bp.route('', methods=['GET'])
def search_tickers():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    port = _get_ticker_search()
    results = port.search_tickers(query)
    return jsonify({'results': results})