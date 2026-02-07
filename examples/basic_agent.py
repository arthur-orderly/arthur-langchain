"""
Basic example: LangChain agent that trades on Arthur DEX.

Prerequisites:
    pip install arthur-langchain langchain-openai

Environment variables:
    OPENAI_API_KEY=sk-...
    ORDERLY_ACCOUNT_ID=0x...
    ORDERLY_KEY=ed25519:...
    ORDERLY_SECRET=your_base58_secret
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from arthur_langchain import ArthurDEXToolkit

# Get all Arthur DEX tools
toolkit = ArthurDEXToolkit()
tools = toolkit.get_tools()

# Create agent
llm = ChatOpenAI(model="gpt-4o")
agent = create_react_agent(llm, tools)

# Run it
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What markets are available on Arthur DEX? Show me the top 5."}]}
)

for msg in result["messages"]:
    print(f"{msg.type}: {msg.content[:200] if msg.content else '(tool call)'}")

# More examples:
# agent.invoke({"messages": [{"role": "user", "content": "Buy 0.01 BTC perps at market"}]})
# agent.invoke({"messages": [{"role": "user", "content": "Show my positions and PnL"}]})
# agent.invoke({"messages": [{"role": "user", "content": "Close my ETH position"}]})
