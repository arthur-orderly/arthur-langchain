"""Arthur DEX Toolkit — bundle all tools for easy agent integration."""

from __future__ import annotations

from langchain_core.tools import BaseTool

from arthur_langchain.tools import (
    ArthurPlaceOrderTool,
    ArthurGetPositionsTool,
    ArthurGetBalanceTool,
    ArthurGetMarketsTool,
    ArthurClosePositionTool,
)


class ArthurDEXToolkit:
    """
    A toolkit that bundles all Arthur DEX trading tools for LangChain agents.

    Usage:
        toolkit = ArthurDEXToolkit()
        tools = toolkit.get_tools()
        agent = create_react_agent(llm, tools)
    """

    def get_tools(self) -> list[BaseTool]:
        """Return all Arthur DEX tools."""
        return [
            ArthurPlaceOrderTool(),
            ArthurGetPositionsTool(),
            ArthurGetBalanceTool(),
            ArthurGetMarketsTool(),
            ArthurClosePositionTool(),
        ]
