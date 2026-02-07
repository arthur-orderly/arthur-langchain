"""LangChain tools for trading on Arthur DEX via Orderly Network."""

from __future__ import annotations

import json
import os
from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


def _get_client() -> Any:
    """Create an OrderlyClient from environment variables."""
    from arthur_sdk import OrderlyClient

    return OrderlyClient(
        account_id=os.environ["ORDERLY_ACCOUNT_ID"],
        orderly_key=os.environ["ORDERLY_KEY"],
        orderly_secret=os.environ["ORDERLY_SECRET"],
        broker_id=os.environ.get("ORDERLY_BROKER_ID", "arthur"),
    )


# ── Input Schemas ────────────────────────────────────────


class PlaceOrderInput(BaseModel):
    """Input for placing an order on Arthur DEX."""

    symbol: str = Field(
        description="Trading pair symbol, e.g. 'PERP_BTC_USDC', 'PERP_ETH_USDC'"
    )
    side: str = Field(description="Order side: 'BUY' or 'SELL'")
    order_type: str = Field(
        default="MARKET",
        description="Order type: 'MARKET', 'LIMIT', 'IOC', 'FOK', 'POST_ONLY'",
    )
    quantity: float = Field(description="Order quantity (e.g. 0.01 for BTC)")
    price: Optional[float] = Field(
        default=None, description="Limit price (required for LIMIT orders)"
    )


class ClosePositionInput(BaseModel):
    """Input for closing a position."""

    symbol: str = Field(
        description="Trading pair symbol to close, e.g. 'PERP_BTC_USDC'"
    )


class MarketFilterInput(BaseModel):
    """Optional filter for markets."""

    symbol_filter: Optional[str] = Field(
        default=None,
        description="Optional substring to filter markets (e.g. 'BTC')",
    )


# ── Tools ────────────────────────────────────────────────


class ArthurPlaceOrderTool(BaseTool):
    """Place a market or limit order on Arthur DEX (Orderly Network)."""

    name: str = "arthur_place_order"
    description: str = (
        "Place a perpetual futures order on Arthur DEX. "
        "Supports MARKET and LIMIT orders. "
        "Example: symbol='PERP_BTC_USDC', side='BUY', quantity=0.01"
    )
    args_schema: Type[BaseModel] = PlaceOrderInput

    def _run(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
    ) -> str:
        client = _get_client()
        try:
            result = client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error placing order: {e}"


class ArthurGetPositionsTool(BaseTool):
    """View open positions on Arthur DEX."""

    name: str = "arthur_get_positions"
    description: str = (
        "Get all open perpetual futures positions on Arthur DEX with PnL, "
        "entry price, mark price, and liquidation price."
    )

    def _run(self) -> str:
        client = _get_client()
        try:
            positions = client.get_positions()
            if hasattr(positions, "get"):
                rows = positions.get("rows", positions)
            else:
                rows = positions
            open_pos = [p for p in rows if isinstance(p, dict) and p.get("position_qty", 0) != 0]
            if not open_pos:
                return "No open positions."
            return json.dumps(open_pos, default=str)
        except Exception as e:
            return f"Error fetching positions: {e}"


class ArthurGetBalanceTool(BaseTool):
    """Check account balance on Arthur DEX."""

    name: str = "arthur_get_balance"
    description: str = (
        "Check your USDC and token balances on Arthur DEX (Orderly Network)."
    )

    def _run(self) -> str:
        client = _get_client()
        try:
            balances = client.get_balances()
            if hasattr(balances, "get"):
                holding = balances.get("holding", balances)
            else:
                holding = balances
            return json.dumps(holding, default=str)
        except Exception as e:
            return f"Error fetching balances: {e}"


class ArthurGetMarketsTool(BaseTool):
    """List available markets on Arthur DEX."""

    name: str = "arthur_get_markets"
    description: str = (
        "List available perpetual futures markets on Arthur DEX with "
        "current prices, 24h volume, and funding rates. "
        "Optionally filter by symbol substring."
    )
    args_schema: Type[BaseModel] = MarketFilterInput

    def _run(self, symbol_filter: Optional[str] = None) -> str:
        client = _get_client()
        try:
            data = client.get_futures() if hasattr(client, "get_futures") else None
            if data is None:
                # Fallback: use requests directly for public endpoint
                import requests
                resp = requests.get("https://api-evm.orderly.org/v1/public/futures")
                data = resp.json().get("data", {})

            rows = data.get("rows", data) if isinstance(data, dict) else data
            if symbol_filter:
                rows = [r for r in rows if symbol_filter.upper() in r.get("symbol", "")]

            # Return top 15 by volume
            rows = sorted(rows, key=lambda r: r.get("24h_volume", 0), reverse=True)[:15]
            summary = [
                {
                    "symbol": r["symbol"],
                    "mark_price": r.get("mark_price"),
                    "24h_volume": r.get("24h_volume"),
                    "funding_rate": r.get("est_funding_rate"),
                }
                for r in rows
            ]
            return json.dumps(summary, default=str)
        except Exception as e:
            return f"Error fetching markets: {e}"


class ArthurClosePositionTool(BaseTool):
    """Close an open position on Arthur DEX."""

    name: str = "arthur_close_position"
    description: str = (
        "Close an open perpetual futures position on Arthur DEX by "
        "placing an opposing market order. Specify the symbol to close."
    )
    args_schema: Type[BaseModel] = ClosePositionInput

    def _run(self, symbol: str) -> str:
        client = _get_client()
        try:
            # Get current position to determine side and quantity
            positions = client.get_positions()
            rows = positions.get("rows", positions) if isinstance(positions, dict) else positions
            pos = next((p for p in rows if isinstance(p, dict) and p.get("symbol") == symbol and p.get("position_qty", 0) != 0), None)

            if not pos:
                return f"No open position for {symbol}"

            qty = abs(pos["position_qty"])
            side = "SELL" if pos["position_qty"] > 0 else "BUY"

            result = client.place_order(
                symbol=symbol,
                side=side,
                order_type="MARKET",
                quantity=qty,
                reduce_only=True,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error closing position: {e}"
