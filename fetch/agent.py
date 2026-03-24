import json
import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

load_dotenv()
LLM_MODEL = os.getenv("MODEL", "gemini-flash-lite-latest")
DESCRIPTION = "Agent for fetching web page"
INSTRUCTION = """
You are an agent that fetches and processes web page contents.
You have access to a Fetch MCP server which provides tools to retrieve web pages.

**Responsibilities**:
1. When asked to fetch or read a URL, use the available MCP tool to retrieve the content.
2. If the user asks specific questions about the content, extract the relevant information and present it clearly.
3. If the user asks for a summary, summarize the fetched content concisely.
4. Handle fetch errors gracefully and inform the user if a page cannot be accessed.

Language Policy: Regardless of the user's language, you MUST respond in **Korean**.
"""


# --- Load MCP Configuration ---
mcp_config_path = os.path.join(os.path.dirname(__file__), "mcp.json")
with open(mcp_config_path, "r") as f:
    mcp_config = json.load(f)

mcp_server_config = mcp_config.get("mcpServers", {}).get("fetch-mcp", {})

# --- Agent Definitions ---

# Agent for fetching and processing web page content.
# It uses the Fetch MCP server to retrieve web pages.
root_agent = Agent(
    name="RootAgent",
    model=LLM_MODEL,
    instruction=INSTRUCTION,
    description=DESCRIPTION,
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command=mcp_server_config.get("command"),
                args=mcp_server_config.get("args"),
                env=mcp_server_config.get("env"),
                timeout=30,
            ),
        ),
    ],
)
