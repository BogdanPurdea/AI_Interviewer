from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# Simple in-memory storage for now. 
# In production, this would be Redis, Postgres, etc.
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Returns the chat history for a given session ID."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def clear_session_history(session_id: str):
    """Clears the history for a session."""
    if session_id in store:
        del store[session_id]
