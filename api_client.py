import requests
import logging

class APIClient:
    """
    Client to interact with the MCP Agent backend API.
    """
    def __init__(self, api_url: str, agent_name: str, user_id: str):
        self.api_url = api_url
        self.agent_name = agent_name
        self.user_id = user_id

    def _get_session_url(self, session_id: str) -> str:
        return f"{self.api_url}/apps/{self.agent_name}/users/{self.user_id}/sessions/{session_id}"

    def create_session(self, session_id: str):
        """Creates a new session for the agent."""
        try:
            url = self._get_session_url(session_id)
            response = requests.post(url)
            return response
        except Exception as e:
            logging.error(f"Error creating session: {e}")
            raise

    def delete_session(self, session_id: str):
        """Deletes an existing session."""
        try:
            url = self._get_session_url(session_id)
            response = requests.delete(url)
            return response
        except Exception as e:
            logging.error(f"Error deleting session: {e}")
            raise

    def run_agent(self, session_id: str, query_text: str):
        """Sends a message to the agent and gets a response."""
        try:
            url = f"{self.api_url}/run"
            payload = {
                "app_name": self.agent_name,
                "user_id": self.user_id,
                "session_id": session_id,
                "new_message": {
                    "role": "user",
                    "parts": [{"text": query_text}]
                }
            }
            response = requests.post(url, json=payload)
            return response
        except Exception as e:
            logging.error(f"Error running agent: {e}")
            raise
