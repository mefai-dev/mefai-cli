"""HTTP client wrapper for MEFAI Engine API.

All outbound requests go through the MefaiClient class which
handles authentication headers and base URL resolution.
"""

from typing import Any

import httpx

from mefai_cli.config import get_api_key, get_base_url


class MefaiClient:
    """Synchronous HTTP client for the MEFAI Engine REST API."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self.api_key = api_key or get_api_key()
        self._headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "mefai-cli/0.1.0",
        }
        if self.api_key:
            self._headers["Authorization"] = f"Bearer {self.api_key}"

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a GET request and return the JSON body."""
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(self._url(path), headers=self._headers, params=params)
            resp.raise_for_status()
            return resp.json()  # type: ignore[no-any-return]

    def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a POST request and return the JSON body."""
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(self._url(path), headers=self._headers, json=json)
            resp.raise_for_status()
            return resp.json()  # type: ignore[no-any-return]

    def delete(self, path: str) -> dict[str, Any]:
        """Send a DELETE request and return the JSON body."""
        with httpx.Client(timeout=30.0) as client:
            resp = client.delete(self._url(path), headers=self._headers)
            resp.raise_for_status()
            return resp.json()  # type: ignore[no-any-return]

    def health_check(self) -> dict[str, Any]:
        """Ping the /health endpoint."""
        return self.get("/health")

    def engine_status(self) -> dict[str, Any]:
        """Fetch engine status."""
        return self.get("/api/v1/status")

    def positions(self) -> dict[str, Any]:
        """Fetch open positions."""
        return self.get("/api/v1/positions")

    def balance(self) -> dict[str, Any]:
        """Fetch account balance."""
        return self.get("/api/v1/balance")

    def ticker(self, symbol: str) -> dict[str, Any]:
        """Fetch ticker price for a symbol."""
        return self.get(f"/api/v1/ticker/{symbol}")

    def orderbook(self, symbol: str) -> dict[str, Any]:
        """Fetch order book for a symbol."""
        return self.get(f"/api/v1/orderbook/{symbol}")

    def funding_rate(self, symbol: str) -> dict[str, Any]:
        """Fetch funding rate for a symbol."""
        return self.get(f"/api/v1/funding/{symbol}")

    def candles(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> dict[str, Any]:
        """Fetch candlestick data."""
        return self.get(f"/api/v1/candles/{symbol}", params={"timeframe": timeframe, "limit": limit})

    def features(self, symbol: str) -> dict[str, Any]:
        """Fetch computed features for a symbol."""
        return self.get(f"/api/v1/features/{symbol}")

    def signals(self) -> dict[str, Any]:
        """Fetch active signals."""
        return self.get("/api/v1/signals")

    def models(self) -> dict[str, Any]:
        """List available ML models."""
        return self.get("/api/v1/models")

    def predict(self, symbol: str, model: str | None = None) -> dict[str, Any]:
        """Run prediction on a symbol."""
        params: dict[str, Any] = {}
        if model:
            params["model"] = model
        return self.get(f"/api/v1/predict/{symbol}", params=params)

    def backtest(self, symbol: str, start: str | None = None, end: str | None = None) -> dict[str, Any]:
        """Run backtest on a symbol."""
        payload: dict[str, Any] = {"symbol": symbol}
        if start:
            payload["start"] = start
        if end:
            payload["end"] = end
        return self.post("/api/v1/backtest", json=payload)

    def metrics(self) -> dict[str, Any]:
        """Fetch PnL metrics."""
        return self.get("/api/v1/metrics")

    def risk(self) -> dict[str, Any]:
        """Fetch risk status."""
        return self.get("/api/v1/risk")

    def report(self) -> dict[str, Any]:
        """Generate daily report."""
        return self.post("/api/v1/report")

    def place_order(self, symbol: str, side: str, quantity: float) -> dict[str, Any]:
        """Place an order."""
        return self.post("/api/v1/orders", json={
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
        })

    def close_position(self, symbol: str) -> dict[str, Any]:
        """Close an open position."""
        return self.post(f"/api/v1/positions/{symbol}/close")
