import os
from datetime import timedelta
from dotenv import load_dotenv
import pymongo

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    
    # MongoDB settings (replace SQL)
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/ecommerce_db")
    client = pymongo.MongoClient(MONGO_URI)
    db = client.get_database()  # Automatically uses DB name from URI (e.g., ecommerce_db)

    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change-in-production"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

    PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "ecommerce-products")

    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}