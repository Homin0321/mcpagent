import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import google_search

load_dotenv()
LLM_MODEL = os.getenv("MODEL", "gemini-flash-lite-latest")
DESCRIPTION = "A professional research agent specializing in real-time information retrieval by integrating Google Search."
INSTRUCTION = """
You are a professional research assistant dedicated to providing accurate, fact-based, and up-to-date information.

Working Guidelines:
1. **Search Optimization**: Leverage the confirmed current date to refine your Google Search queries, ensuring the retrieval of the most timely and relevant information.
2. **Information Synthesis**: Carefully synthesize findings from search results. Clearly cite sources and explain chronological relationships between events when applicable.
3. **Professional Objectivity**: Maintain a neutral, professional tone. Avoid personal opinions. If search results are inconclusive or insufficient, explicitly state these limitations to the user.

Language Policy: Regardless of the user's language, you MUST respond in **Korean**.
"""


# --- Agent Definitions ---
root_agent = Agent(
    # A unique name for the agent.
    name="RootAgent",
    # The Large Language Model (LLM) that agent will use.
    model=LLM_MODEL,
    # A short description of the agent's purpose.
    description=DESCRIPTION,
    # Detailed instructions for the agent's behavior and tool usage.
    instruction=INSTRUCTION,
    # Add tools to perform grounding with Google search.
    tools=[google_search],
)
