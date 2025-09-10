import json
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class ChatSession(BaseModel):
    id: str
    user_id: Optional[str] = None
    session_data: str = "{}"  # Stored as JSON string
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    messages: List[str] = []  # List of message IDs

    class Config:
        arbitrary_types_allowed = True

    def get_session_data(self):
        """Get session data as dict"""
        try:
            return json.loads(self.session_data) if self.session_data else {}
        except json.JSONDecodeError:
            return {}

    def set_session_data(self, data_dict):
        """Set session data from dict"""
        self.session_data = json.dumps(data_dict)
        self.updated_at = datetime.now()

    def get_message_count(self):
        """Get total message count in session"""
        return len(self.messages)

    def get_recent_messages(self, limit=10):
        """Placeholder for recent messages (manual lookup needed in service)"""
        # In MongoDB, this would require a separate query or embedded messages
        return self.messages[-limit:] if len(self.messages) > limit else self.messages

    def to_dict(self, include_messages=False):
        """Convert chat session to dictionary"""
        data = {
            "id": self.id,
            "userId": self.user_id,
            "sessionData": self.get_session_data(),
            "messageCount": self.get_message_count(),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "isActive": self.is_active,
        }
        if include_messages:
            data["messages"] = self.messages  # IDs only, or expand if embedded
        return data

    def __repr__(self):
        return f"<ChatSession {self.id}>"