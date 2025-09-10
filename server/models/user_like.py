from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserLike(BaseModel):
    id: str
    user_id: str
    product_id: str
    created_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }