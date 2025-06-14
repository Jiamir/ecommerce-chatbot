from .auth_routes import auth_bp
from .product_routes import product_bp
from .chat_routes import chat_bp
from .cart_routes import cart_bp


def register_routes(app):
    """Register all route blueprints"""
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(cart_bp, url_prefix="/api")
