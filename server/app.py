import os

from config import config
from dotenv import load_dotenv
from flask import Flask, jsonify, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from utils.logger_config import setup_logging

# Import MongoDB db from config
from config import Config as AppConfig  # To access db
from utils.database_seeder import DatabaseSeeder

load_dotenv()

jwt = JWTManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    jwt.init_app(app)

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    setup_logging(app)

    from routes import register_routes

    register_routes(app)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "message": "Bad request"}), 400

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"success": False, "message": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify(
            {"success": False, "message": "Authorization token is required"}
        ), 401

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify(
            {
                "success": True,
                "status": "healthy",
                "message": "E-commerce Chatbot API is running",
            }
        ), 200

    @app.before_request
    def initialize_database():
        """Initialize database and seed with sample data if empty"""
        if not hasattr(g, 'seeded'):
            try:
                db = AppConfig.db  # MongoDB db
                if db["products"].count_documents({}) == 0:  # Check if empty
                    seeder = DatabaseSeeder()  # Correct instantiation
                    seeder.seed_products()
                    seeder.seed_users()  # Seed users too

                app.logger.info("Database initialized successfully")
            except Exception as e:
                app.logger.error(f"Error initializing database: {str(e)}")
                if app.config["DEBUG"]:  # Re-raise in debug mode
                    raise
            finally:
                g.seeded = True  # Ensure this runs even on error

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
        threaded=True
    )