# arthur-langchain

> LangChain tools for trading perpetuals on [Arthur DEX](https://arthurdex.com) — plug into any LangChain/LangGraph agent.

## Install

```bash
pip install arthur-langchain
```

## Quick Start

```python
from arthur_langchain import ArthurDEXToolkit
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

tools = ArthurDEXToolkit().get_tools()
agent = create_react_agent(ChatOpenAI(model="gpt-4o"), tools)
agent.invoke({"messages": [{"role": "user", "content": "Buy 0.01 BTC perps"}]})
```

5 lines. Your agent can now trade perps.

## Configuration

Set these environment variables:

| Variable | Description |
|----------|-------------|
| `ORDERLY_ACCOUNT_ID` | Your Orderly account ID (hex) |
| `ORDERLY_KEY` | ed25519 public key (`ed25519:...`) |
| `ORDERLY_SECRET` | ed25519 secret key (base58) |
| `ORDERLY_BROKER_ID` | Broker ID (default: `arthur`) |

Get your keys at [arthurdex.com](https://arthurdex.com) → connect wallet → generate API keys.

## Available Tools

| Tool | Description |
|------|-------------|
| `arthur_place_order` | Place market/limit perp orders (symbol, side, quantity, price) |
| `arthur_get_positions` | View open positions with PnL, entry/mark price, liq price |
| `arthur_get_balance` | Check USDC and token balances |
| `arthur_get_markets` | List markets with prices, volume, funding rates |
| `arthur_close_position` | Close a position via opposing market order |

## Use Individual Tools

```python
from arthur_langchain import ArthurPlaceOrderTool, ArthurGetMarketsTool

# Add specific tools to your agent
tools = [ArthurGetMarketsTool(), ArthurPlaceOrderTool()]
```

## Use with LangGraph

```python
from langgraph.prebuilt import create_react_agent
from arthur_langchain import ArthurDEXToolkit

tools = ArthurDEXToolkit().get_tools()
agent = create_react_agent(llm, tools)

# The agent decides which tools to call based on the user's message
result = agent.invoke({"messages": [{"role": "user", "content": "What's my PnL?"}]})
```

## Links

- 🏠 [Arthur DEX](https://arthurdex.com)
- 📦 [Arthur SDK](https://pypi.org/project/arthur-sdk/)
- 🦜 [LangChain](https://python.langchain.com)
- 📖 [Orderly Docs](https://docs.orderly.network)

## License

MIT
