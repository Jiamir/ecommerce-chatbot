import json
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from werkzeug.security import check_password_hash, generate_password_hash

class User(BaseModel):
    id: str
    email: str
    name: str
    password_hash: str
    preferences: str = '{"favoriteCategories": [], "priceRange": [0, 2000], "favoriteBrands": []}'  # JSON string
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    chat_sessions: List[str] = []  # List of chat session IDs

    class Config:
        arbitrary_types_allowed = True

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def get_preferences(self):
        """Get user preferences as dict"""
        try:
            return json.loads(self.preferences) if self.preferences else {}
        except json.JSONDecodeError:
            return {}

    def set_preferences(self, preferences_dict):
        """Set user preferences from dict"""
        self.preferences = json.dumps(preferences_dict)
        self.updated_at = datetime.now()

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "preferences": self.get_preferences(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
        }

    def __repr__(self):
        return f"<User {self.email}>"