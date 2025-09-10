import logging
from typing import List, Dict, Any, Optional
from models.product import Product
from .vector_service import VectorService
from config import Config as AppConfig  # For db
from datetime import datetime
from pymongo import DESCENDING

logger = logging.getLogger(__name__)

class ProductService:
    """Service for product-related operations"""

    def __init__(self):
        self.vector_service = VectorService()
        self.db = AppConfig.db
        self.collection = self.db["products"]

    def create_product(self, product_data: Dict[str, Any]) -> Product:
        """Create a new product and generate its embedding"""
        try:
            product = Product(**product_data)
            product.created_at = datetime.now()
            product.updated_at = datetime.now()

            self.collection.insert_one(product.dict())

            search_text = product.get_search_text()
            metadata = {
                "category": product.category,
                "subcategory": product.subcategory,
                "brand": product.brand,
                "price": product.price,
                "rating": product.rating,
                "in_stock": product.is_in_stock(),
            }

            self.vector_service.upsert_product_embedding(
                product.id, search_text, metadata
            )

            self.collection.update_one(
                {"id": product.id},
                {"$set": {"embedding_id": product.id}}
            )

            logger.info(f"Created product: {product.name}")
            return product

        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    def update_product(
        self, product_id: str, update_data: Dict[str, Any]
    ) -> Optional[Product]:
        """Update a product and refresh its embedding"""
        try:
            existing_doc = self.collection.find_one({"id": product_id})
            if not existing_doc:
                return None

            product = Product(**existing_doc)
            for key, value in update_data.items():
                if hasattr(product, key):
                    setattr(product, key, value)

            product.updated_at = datetime.now()

            content_fields = [
                "name",
                "description",
                "features",
                "category",
                "subcategory",
                "brand",
            ]
            if any(field in update_data for field in content_fields):
                search_text = product.get_search_text()
                metadata = {
                    "category": product.category,
                    "subcategory": product.subcategory,
                    "brand": product.brand,
                    "price": product.price,
                    "rating": product.rating,
                    "in_stock": product.is_in_stock(),
                }

                self.vector_service.upsert_product_embedding(
                    product.id, search_text, metadata
                )

            self.collection.replace_one({"id": product_id}, product.dict())

            logger.info(f"Updated product: {product.name}")
            return product

        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise

    def delete_product(self, product_id: str) -> bool:
        """Delete a product and its embedding"""
        try:
            existing_doc = self.collection.find_one({"id": product_id})
            if not existing_doc:
                return False

            self.vector_service.delete_product_embedding(product_id)

            self.collection.delete_one({"id": product_id})

            logger.info(f"Deleted product: {existing_doc['name']}")
            return True

        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            raise

    def search_products(
        self, query: str, filters: Dict[str, Any] = None, limit: int = 20
    ) -> List[Product]:
        """Search products using both vector similarity and traditional filters"""
        try:
            vector_results = self.vector_service.search_similar_products(
                query,
                top_k=limit * 2,
            )

            if not vector_results:
                return self.search_by_filters(search_query=query, limit=limit)

            product_ids = [result["id"] for result in vector_results]

            mongo_filter = {"id": {"$in": product_ids}}

            if filters:
                if filters.get("category"):
                    mongo_filter["category"] = filters["category"]

                if filters.get("subcategory"):
                    mongo_filter["subcategory"] = filters["subcategory"]

                if filters.get("brand"):
                    mongo_filter["brand"] = filters["brand"]

                if filters.get("min_price") is not None:
                    mongo_filter["price"] = {"$gte": filters["min_price"]}

                if filters.get("max_price") is not None:
                    if "price" not in mongo_filter:
                        mongo_filter["price"] = {}
                    mongo_filter["price"]["$lte"] = filters["max_price"]

                if filters.get("min_rating") is not None:
                    mongo_filter["rating"] = {"$gte": filters["min_rating"]}

                if filters.get("in_stock_only"):
                    mongo_filter["stock"] = {"$gt": 0}

            docs = list(self.collection.find(mongo_filter))

            products = [Product(**doc) for doc in docs]

            product_score_map = {
                result["id"]: result["score"] for result in vector_results
            }
            products.sort(key=lambda p: product_score_map.get(p.id, 0), reverse=True)

            return products[:limit]

        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []

    def get_recommendations(
        self,
        product_id: str = None,
        user_preferences: Dict[str, Any] = None,
        limit: int = 6,
    ) -> List[Product]:
        """Get product recommendations"""
        try:
            if product_id:
                doc = self.collection.find_one({"id": product_id})
                if not doc:
                    return []

                product = Product(**doc)
                search_text = product.get_search_text()
                similar_results = self.vector_service.search_similar_products(
                    search_text,
                    top_k=limit + 1,
                )

                similar_ids = [
                    r["id"] for r in similar_results if r["id"] != product_id
                ]

            elif user_preferences:
                pref_text = self._build_preference_text(user_preferences)
                similar_results = self.vector_service.search_similar_products(
                    pref_text, top_k=limit
                )
                similar_ids = [r["id"] for r in similar_results]

            else:
                docs = list(self.collection.find({"is_active": True}).sort("rating", DESCENDING).limit(limit))
                return [Product(**doc) for doc in docs]

            docs = list(self.collection.find({"id": {"$in": similar_ids}}))

            products = [Product(**doc) for doc in docs]

            if similar_results:
                score_map = {r["id"]: r["score"] for r in similar_results}
                products.sort(key=lambda p: score_map.get(p.id, 0), reverse=True)

            return products[:limit]

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []

    def _build_preference_text(self, preferences: Dict[str, Any]) -> str:
        """Build search text from user preferences"""
        text_parts = []

        if preferences.get("favoriteCategories"):
            text_parts.extend(preferences["favoriteCategories"])

        if preferences.get("favoriteBrands"):
            text_parts.extend(preferences["favoriteBrands"])

        if preferences.get("priceRange"):
            min_price, max_price = preferences["priceRange"]
            if max_price < 500:
                text_parts.append("budget affordable cheap")
            elif max_price > 1500:
                text_parts.append("premium high-end expensive")
            else:
                text_parts.append("mid-range")

        return " ".join(text_parts) if text_parts else "popular electronics"

    def bulk_generate_embeddings(self):
        """Generate embeddings for all products (useful for initial setup)"""
        try:
            docs = list(self.collection.find({"is_active": True}))

            batch_data = []
            for doc in docs:
                product = Product(**doc)
                search_text = product.get_search_text()
                metadata = {
                    "category": product.category,
                    "subcategory": product.subcategory,
                    "brand": product.brand,
                    "price": product.price,
                    "rating": product.rating,
                    "in_stock": product.is_in_stock(),
                }

                batch_data.append(
                    {"id": product.id, "text": search_text, "metadata": metadata}
                )

            self.vector_service.batch_upsert_products(batch_data)

            for doc in docs:
                self.collection.update_one(
                    {"id": doc["id"]},
                    {"$set": {"embedding_id": doc["id"]}}
                )

            logger.info(f"Generated embeddings for {len(docs)} products")
            return len(docs)

        except Exception as e:
            logger.error(f"Error generating bulk embeddings: {str(e)}")
            raise

    # Added from model: search_by_filters
    def search_by_filters(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: bool = False,
        search_query: Optional[str] = None,
        limit: int = 50,
    ) -> List[Product]:
        """Search products with filters"""
        mongo_filter = {"is_active": True}

        if category:
            mongo_filter["category"] = {"$regex": category, "$options": "i"}

        if subcategory:
            mongo_filter["subcategory"] = {"$regex": subcategory, "$options": "i"}

        if brand:
            mongo_filter["brand"] = {"$regex": brand, "$options": "i"}

        if min_price is not None:
            mongo_filter["price"] = {"$gte": min_price}

        if max_price is not None:
            if "price" not in mongo_filter:
                mongo_filter["price"] = {}
            mongo_filter["price"]["$lte"] = max_price

        if min_rating is not None:
            mongo_filter["rating"] = {"$gte": min_rating}

        if in_stock_only:
            mongo_filter["stock"] = {"$gt": 0}

        if search_query:
            mongo_filter["$or"] = [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"description": {"$regex": search_query, "$options": "i"}},
                {"brand": {"$regex": search_query, "$options": "i"}},
                {"features": {"$regex": search_query, "$options": "i"}},
            ]

        docs = list(self.collection.find(mongo_filter).sort("rating", DESCENDING).limit(limit))
        return [Product(**doc) for doc in docs]