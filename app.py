import os
import time
import uuid

import requests
import streamlit as st
from api_client import APIClient
from dotenv import load_dotenv, set_key
from utils import fix_markdown_symbol_issue

load_dotenv()

agent_options = ["fastjira", "gemini", "search", "url", "jira0", "collab", "googleapis"]
model_options = [
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

# Set Streamlit page configuration
st.set_page_config(page_title="MCP Agent", page_icon="🤖", layout="wide")


def init_session_state():
    """Initialize session state variables if they don't exist."""
    if "sessions" not in st.session_state:
        # Dictionary to store multiple sessions
        # Format: { "session_id": { "name": "Session 1", "chat_history": [], "agent": "gemini" } }
        st.session_state.sessions = {}
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "session_counter" not in st.session_state:
        st.session_state.session_counter = 1
    if "last_response" not in st.session_state:
        st.session_state.last_response = None


# --- Application Initialization ---
init_session_state()

# Determine the current agent based on the active session, or default to the first option
current_agent = agent_options[0]
if (
    st.session_state.current_session_id
    and st.session_state.current_session_id in st.session_state.sessions
):
    current_agent = st.session_state.sessions[st.session_state.current_session_id][
        "agent"
    ]

# Initialize API Client
client = APIClient("http://localhost:8000", current_agent, "user")


def create_new_session_flow():
    """
    Logic to handle the lifecycle of a session:
    1. Generate a new session ID.
    2. Register the new session on the backend.
    3. Add the session to the local session state.
    """
    st.session_state.last_response = None

    try:
        # Create a new session with a new session ID
        new_session_id = uuid.uuid4().hex
        res = client.create_session(new_session_id)

        if res.status_code == 200:
            st.session_state.sessions[new_session_id] = {
                "name": f"Session {st.session_state.session_counter}",
                "chat_history": [],
                "agent": current_agent,
            }
            st.session_state.current_session_id = new_session_id
            st.session_state.session_counter += 1
            return True
        else:
            st.error(f"Session creation failed: {res.status_code}\n{res.text}")
            return False
    except Exception as e:
        st.error(f"Error during session creation: {e}")
        return False


def delete_session(session_id):
    """Deletes a session from the backend and local state."""
    try:
        client.delete_session(session_id)
    except Exception:
        # Proceed even if delete fails on the backend
        pass

    if session_id in st.session_state.sessions:
        del st.session_state.sessions[session_id]

    # If the active session was deleted, switch to another or set to None
    if st.session_state.current_session_id == session_id:
        if st.session_state.sessions:
            st.session_state.current_session_id = list(
                st.session_state.sessions.keys()
            )[0]
        else:
            st.session_state.current_session_id = None


@st.dialog("Markdown Code", width="large")
def show_markdown_dialog():
    """Displays the raw markdown source of assistant messages with navigation."""
    if (
        st.session_state.current_session_id
        and st.session_state.current_session_id in st.session_state.sessions
    ):
        chat_history = st.session_state.sessions[st.session_state.current_session_id][
            "chat_history"
        ]
        if chat_history:
            assistant_messages = [m for m in chat_history if m["role"] == "assistant"]
            if assistant_messages:
                total_msgs = len(assistant_messages)

                if "md_dialog_idx" not in st.session_state:
                    st.session_state.md_dialog_idx = total_msgs - 1

                # Ensure index is within bounds
                if st.session_state.md_dialog_idx >= total_msgs:
                    st.session_state.md_dialog_idx = total_msgs - 1
                elif st.session_state.md_dialog_idx < 0:
                    st.session_state.md_dialog_idx = 0

                idx = st.session_state.md_dialog_idx

                def go_prev():
                    st.session_state.md_dialog_idx -= 1

                def go_next():
                    st.session_state.md_dialog_idx += 1

                col1, col2, col3 = st.columns([1, 3, 1])

                with col1:
                    st.button(
                        "⬅️ Prev",
                        disabled=(idx <= 0),
                        on_click=go_prev,
                        use_container_width=True,
                    )

                with col2:
                    st.markdown(
                        f"<div style='text-align: center; padding-top: 5px;'>Message {idx + 1} of {total_msgs}</div>",
                        unsafe_allow_html=True,
                    )

                with col3:
                    st.button(
                        "Next ➡️",
                        disabled=(idx >= total_msgs - 1),
                        on_click=go_next,
                        use_container_width=True,
                    )

                st.code(assistant_messages[idx]["content"], language="markdown")
                return

    st.info("No assistant messages to display.")


# --- Sidebar UI ---
st.sidebar.header("MCP Agent")

if st.sidebar.button("Create New Session", use_container_width=True):
    if create_new_session_flow():
        st.rerun()

session_to_switch = None
session_to_delete = None

# Display the list of sessions
for sid in list(st.session_state.sessions.keys()):
    sdata = st.session_state.sessions[sid]
    is_current = sid == st.session_state.current_session_id

    col1, col2 = st.sidebar.columns([4, 1])

    with col1:
        btn_label = f"{'🟢 ' if is_current else ''}{sdata['name']}"
        if st.button(btn_label, key=f"switch_{sid}", use_container_width=True):
            session_to_switch = sid

    with col2:
        if st.button(
            "🗑️", key=f"del_{sid}", use_container_width=True, help="Delete this session"
        ):
            session_to_delete = sid

if session_to_switch:
    st.session_state.current_session_id = session_to_switch
    st.rerun()

if session_to_delete:
    delete_session(session_to_delete)
    st.rerun()


# Agent selection radio button for the CURRENT session
if st.session_state.current_session_id:
    selected_agent = st.sidebar.radio(
        "Select Agent",
        options=agent_options,
        index=agent_options.index(
            st.session_state.sessions[st.session_state.current_session_id]["agent"]
        ),
    )

    # If the agent is changed, update the state but keep the session and history
    if (
        selected_agent
        != st.session_state.sessions[st.session_state.current_session_id]["agent"]
    ):
        st.session_state.sessions[st.session_state.current_session_id]["agent"] = (
            selected_agent
        )
        # Ensure the backend is aware of the current session for the newly selected agent
        try:
            # We register the existing session ID with the new agent
            APIClient("http://localhost:8000", selected_agent, "user").create_session(
                st.session_state.current_session_id
            )
        except Exception:
            # If registration fails, we still proceed to maintain UI state
            pass
        st.rerun()

if st.sidebar.button("Show Markdown Code", use_container_width=True):
    if "md_dialog_idx" in st.session_state:
        del st.session_state.md_dialog_idx
    show_markdown_dialog()

# Model selection
env_path = os.path.join(os.path.dirname(__file__), ".env")
current_model = os.getenv("MODEL", model_options[0])
if current_model not in model_options:
    model_options.append(current_model)

selected_model = st.sidebar.selectbox(
    "Select Model",
    options=model_options,
    index=model_options.index(current_model),
)


def restart_api_server():
    with st.spinner("Restarting API Server..."):
        try:
            os.system("pkill -f 'adk api_server'")
            time.sleep(1)
            os.system("nohup adk api_server > /dev/null 2>&1 &")
            time.sleep(2)
            st.sidebar.success("API Server restarted!")
        except Exception as e:
            st.sidebar.error(f"Failed to restart: {e}")


if selected_model != current_model:
    if not os.path.exists(env_path):
        open(env_path, "a").close()
    set_key(env_path, "MODEL", selected_model)
    os.environ["MODEL"] = selected_model
    restart_api_server()
    st.rerun()

if st.sidebar.button("Restart API Server", use_container_width=True):
    restart_api_server()

# Automatically create a session on first load if one doesn't exist
if st.session_state.current_session_id is None:
    if create_new_session_flow():
        st.rerun()


# --- Main Chat Interface ---

# Ensure we have an active session before attempting to render chat
if (
    st.session_state.current_session_id
    and st.session_state.current_session_id in st.session_state.sessions
):
    chat_history = st.session_state.sessions[st.session_state.current_session_id][
        "chat_history"
    ]

    # Use a container to manage chat history display
    chat_container = st.container()

    # 1. Display existing chat history within the container
    with chat_container:
        for msg in chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 2. User input box
    if query_text := st.chat_input("Enter your question"):
        # If this is the first message in the session, update the session name
        current_session_data = st.session_state.sessions[
            st.session_state.current_session_id
        ]
        if len(current_session_data["chat_history"]) == 0:
            new_name = query_text[:20] + "..." if len(query_text) > 20 else query_text
            current_session_data["name"] = new_name

        # Display the user's question immediately without adding to session state yet
        with chat_container:
            with st.chat_message("user"):
                st.markdown(query_text)

            # 3. Process request via Backend API inside the assistant message block
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        res = client.run_agent(
                            st.session_state.current_session_id, query_text
                        )

                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.last_response = (
                                data  # Save full response for debugging
                            )

                            if data and isinstance(data, list):
                                final_text = ""
                                # Robustly extract the final assistant text from the response array
                                for message in reversed(data):
                                    content = message.get("content", {})
                                    role = message.get("role")
                                    if not role and isinstance(content, dict):
                                        role = content.get("role")

                                    parts = (
                                        content.get("parts", [])
                                        if isinstance(content, dict)
                                        else message.get("parts", [])
                                    )
                                    if not isinstance(parts, list):
                                        continue

                                    for part in parts:
                                        if not isinstance(part, dict):
                                            continue

                                        # Case A: Standard text response
                                        if (
                                            role in ["assistant", "model"]
                                            and "text" in part
                                        ):
                                            candidate_text = part.get(
                                                "text", ""
                                            ).strip()
                                            if candidate_text:
                                                final_text = candidate_text
                                                break

                                        # Case B: Tool execution result (functionResponse)
                                        elif "functionResponse" in part:
                                            response_obj = part.get(
                                                "functionResponse", {}
                                            ).get("response", {})
                                            if isinstance(response_obj, dict):
                                                candidate_text = (
                                                    response_obj.get("result")
                                                    or response_obj.get("text")
                                                    or ""
                                                ).strip()
                                                if candidate_text:
                                                    final_text = candidate_text
                                                    break

                                    if final_text:
                                        break

                                # Show thinking process if multiple steps exist
                                if len(data) > 1:
                                    with st.expander(
                                        "View Thinking Process", expanded=False
                                    ):
                                        st.json(data)

                                if final_text:
                                    fixed_text = fix_markdown_symbol_issue(final_text)
                                    st.markdown(fixed_text)

                                    # Add messages to history ONLY after completion
                                    st.session_state.sessions[
                                        st.session_state.current_session_id
                                    ]["chat_history"].append(
                                        {"role": "user", "content": query_text}
                                    )
                                    st.session_state.sessions[
                                        st.session_state.current_session_id
                                    ]["chat_history"].append(
                                        {"role": "assistant", "content": fixed_text}
                                    )

                                    # Rerun to refresh the chat history display and clear the temporary UI
                                    st.rerun()
                                else:
                                    st.error(
                                        "No assistant text response found in the agent output."
                                    )
                            else:
                                st.warning(
                                    "Received an empty or invalid response format from the agent."
                                )
                        else:
                            st.error(f"Query failed: {res.status_code}")
                            with st.expander("Error details"):
                                st.text(res.text)

                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")
