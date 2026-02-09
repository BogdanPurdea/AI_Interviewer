from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

class HistoryService:
    # Simple in-memory storage for now. 
    # In production, this would be Redis, Postgres, etc.
    _store = {}

    @staticmethod
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        """Returns the chat history for a given session ID."""
        if session_id not in HistoryService._store:
            HistoryService._store[session_id] = ChatMessageHistory()
        return HistoryService._store[session_id]

    @staticmethod
    def clear_session_history(session_id: str):
        """Clears the history for a session."""
        if session_id in HistoryService._store:
            del HistoryService._store[session_id]
