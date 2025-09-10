import json
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class Message(BaseModel):
    id: str
    chat_session_id: str
    content: str
    is_bot: bool = False
    message_type: str = "text"
    products: str = "[]"  # Stored as JSON string
    extra_data: str = "{}"  # Stored as JSON string
    created_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True

    def get_products(self):
        """Get product IDs as list"""
        try:
            return json.loads(self.products) if self.products else []
        except json.JSONDecodeError:
            return []

    def set_products(self, product_ids):
        """Set product IDs from list"""
        self.products = json.dumps(product_ids)

    def get_extra_data(self):
        """Get extra data as dict"""
        try:
            return json.loads(self.extra_data) if self.extra_data else {}
        except json.JSONDecodeError:
            return {}

    def set_extra_data(self, extra_data_dict):
        """Set extra data from dict"""
        self.extra_data = json.dumps(extra_data_dict)

    def to_dict(self, include_product_details=False):
        """Convert message to dictionary"""
        products_data = self.get_products()
        if include_product_details and self.get_products():
            # Placeholder: Requires a service to fetch product details from MongoDB
            products_data = [f"Product_{pid}" for pid in self.get_products()]  # Mock
        data = {
            "id": self.id,
            "chatSessionId": self.chat_session_id,
            "content": self.content,
            "isBot": self.is_bot,
            "type": self.message_type,
            "products": products_data,
            "extraData": self.get_extra_data(),
            "timestamp": self.created_at.isoformat() if self.created_at else None,
        }
        return data

    def __repr__(self):
        return f"<Message {self.id}>"