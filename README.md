# MCP Agent

MCP Agent is an interactive web application built on Streamlit. It leverages the Google ADK (Agent Development Kit) and MCP (Model Context Protocol) to provide an environment for interacting with various specialized AI agents.

## 🌟 Key Features

- **Multi-Session Management**: Independently manage multiple chat sessions by creating, switching, and deleting them.
- **Specialized Agent Selection**: Choose a specialized agent (e.g., basic chat, search, URL analysis) suited for your objective per session.
- **Flexible Model Switching**: Select and change various Gemini models (Flash, Pro, etc.) in real-time from the sidebar.
- **Visualize Agent Thinking Process**: Expand the 'Thinking Process' panel to see how the agent uses tools or performs complex reasoning.
- **Markdown Optimization**: Includes a utility to prevent markdown rendering issues in Streamlit caused by math symbols or special characters. Also supports a 'Show Markdown Code' feature to view raw responses.
- **Backend Server Control**: Restart the API server (`adk api_server`) with a single click from the UI.

## 🤖 Supported Agents

The project includes the following specialized agents:

- **`gemini`**: A basic conversational agent that relies solely on the underlying Large Language Model (LLM) capabilities without real-time information retrieval tools.
- **`search`**: A research agent that utilizes the `google_search` tool to fetch the latest information in real-time and provide fact-based answers.
- **`url`**: An agent that uses the `url_context` tool to extract, analyze, and summarize content from specific web pages provided by the user.
- **`fetch`**: An agent connected to the Fetch MCP server that can directly retrieve and process web page content.
- Other extension agents: `collab`, `jira`, `googleapis` (configurable depending on the environment)

## 📂 Project Structure

```text
mcpagent/
├── app.py               # Main Streamlit frontend application
├── api_client.py        # Client for communicating with the backend server (ADK API)
├── utils.py             # Utility functions, including markdown rendering bug fixes
├── requirements.txt     # List of project dependencies
├── .env                 # Environment variable configuration file (e.g., model name)
├── gemini/              # Folder defining the basic Gemini agent
├── search/              # Folder defining the Google Search specialized agent
├── url/                 # Folder defining the URL analysis specialized agent
└── fetch/               # Folder defining the Fetch MCP tool integration agent
```

## 🛠️ Installation and Setup

1. **Navigate to the directory**
   ```bash
   cd /home/worker/mcpagent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the project root and set the necessary environment variables. (e.g., the default model to use)
   ```env
   MODEL=gemini-flash-lite-latest
   # Add any other required API keys or settings
   ```
   *(Note: Dynamically changing the model via the sidebar in the Streamlit app will automatically update the `.env` file.)*

## 🚀 How to Run

This application operates by separating the backend API server and the frontend UI (Streamlit).

1. **Run the Backend API Server**
   Run the ADK-based API server in the background.
   ```bash
   nohup adk api_server > /dev/null 2>&1 &
   ```
   *(You can also restart the server using the "Restart API Server" button in the app's sidebar.)*

2. **Run the Streamlit Frontend**
   ```bash
   streamlit run app.py
   ```
   Access the application via your browser using the local address printed after running the command (usually `http://localhost:8501`).

## 📝 Operation Notes

- According to the agent's prompt instructions, if the user asks a question in **Korean**, the agent is strictly configured to respond in **Korean**. Otherwise, it defaults to English.
- If a communication error with the backend API or a session management issue occurs, details can be checked through error boxes and the expandable 'Error details' panel in the Streamlit UI.