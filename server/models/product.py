import json
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    original_price: Optional[float] = None
    category: str
    subcategory: str
    brand: str
    rating: float = 0.0
    review_count: int = 0
    image_url: Optional[str] = None
    stock: int = 0
    features: List[str] = []
    is_on_sale: bool = False
    sale_percentage: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    embedding_id: Optional[str] = None

    def get_features(self) -> List[str]:
        """Get features as list"""
        return self.features

    def set_features(self, features_list: List[str]):
        """Set features from list"""
        self.features = features_list
        self.updated_at = datetime.now()

    def get_search_text(self) -> str:
        """Get combined text for embedding generation"""
        features_text = " ".join(self.get_features())
        return f"{self.name} {self.description} {self.brand} {self.category} {self.subcategory} {features_text}"

    def calculate_discount(self) -> int:
        """Calculate discount percentage"""
        if self.original_price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    def is_in_stock(self) -> bool:
        """Check if product is in stock"""
        return self.stock > 0

    def to_dict(self, include_embedding: bool = False) -> Dict[str, Any]:
        """Convert product to dictionary"""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "originalPrice": self.original_price,
            "category": self.category,
            "subcategory": self.subcategory,
            "brand": self.brand,
            "rating": self.rating,
            "reviewCount": self.review_count,
            "imageUrl": self.image_url,
            "stock": self.stock,
            "features": self.get_features(),
            "isOnSale": self.is_on_sale,
            "salePercentage": self.sale_percentage or self.calculate_discount(),
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "isActive": self.is_active,
            "inStock": self.is_in_stock(),
        }

        if include_embedding:
            data["embeddingId"] = self.embedding_id

        return data

    # Removed search_by_filters: Moved to ProductService