import os

from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv()
LLM_MODEL = os.getenv("MODEL", "gemini-flash-lite-latest")
DESCRIPTION = "A helpful and versatile AI assistant capable of handling a wide variety of general tasks."
INSTRUCTION = """
You are a helpful and knowledgeable AI assistant. Your goal is to provide accurate, clear, and helpful answers to the user's questions.

Working Guidelines:
1. **Helpfulness & Clarity**: Provide clear, concise, and highly relevant responses. Break down complex topics if necessary.
2. **Professional Objectivity**: Maintain a polite, neutral, and professional tone. Avoid personal opinions. If you are unsure or do not have enough information, explicitly state these limitations to the user.

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
    # Detailed instructions for the agent's behavior.
    instruction=INSTRUCTION,
)
