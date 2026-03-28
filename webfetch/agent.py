import os
import re

import trafilatura
from dotenv import load_dotenv
from google.adk.agents import Agent
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

load_dotenv()
LLM_MODEL = os.getenv("MODEL", "gemini-3.1-flash-lite-preview")
DESCRIPTION = "A professional web scraping and research agent that extracts text from URLs, formats it as Markdown, translates it to Korean, and answers questions or summarizes based on the web page content."
INSTRUCTION = """
You are a highly capable Web Scraping and Research Agent. You must use the `scrap_url` tool to retrieve text content from specified URLs.

**Core Behaviors based on User Input**:
1. **URL Only (No specific request)**: If the user provides only a URL, extract the text content and output it appropriately formatted as Markdown.
2. **Translation**: If the user asks for a translation, translate the extracted text into Korean while strictly maintaining the original Markdown format.
3. **Summary & Q&A**: If the user asks for a summary or has specific questions, provide accurate answers based ONLY on the extracted web page content.

**Guidelines**:
- Always use the `scrap_url` tool to read the content of any provided URL.
- Do not hallucinate or make up information. Base your responses strictly on the scraped content.
- If the answer is not in the text, explicitly state that the information is missing from the provided URL.
- Language Policy: All your final responses MUST be in **Korean**.
"""


def get_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_youtube_transcript(video_id):
    """Fetches the transcript of a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)

        try:
            # Try to fetch English transcript first
            transcript = transcript_list.find_transcript(["en"])
        except NoTranscriptFound:
            # Fallback: take the first available transcript
            transcript = next(iter(transcript_list))

        return " ".join([item.text for item in transcript.fetch()])

    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None


def scrap_url(url: str) -> str:
    """
    Scrapes a URL and returns the extracted text content.

    Args:
        url: The URL string to scrape.

    Returns:
        The extracted text content from the URL, or an error message if extraction fails.
    """
    video_id = get_video_id(url)
    if video_id:
        transcript = get_youtube_transcript(video_id)
        if transcript:
            return transcript
        else:
            return f"Error: Could not extract transcript from the YouTube video: {url}"

    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        return f"Error: Could not fetch the URL: {url}"

    result = trafilatura.extract(downloaded)
    if result is None:
        return f"Error: Could not extract text from the URL: {url}"

    return result


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
    tools=[scrap_url],
)
