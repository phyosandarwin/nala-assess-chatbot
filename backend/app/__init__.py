from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes import main_bp
from app.core.model_loader import model_resources
from app.core.service_manager import service_manager
import logging

logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """
    Factory function to create and configure the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable Cross-Origin Resource Sharing (CORS)
    CORS(app)

    # Preload models during app startup
    _initialize_models()

    # Initialize shared services
    _initialize_services()

    # Register application routes
    _register_routes(app)

    return app

def _initialize_models():
    """Load embedding and reranker models during app startup."""
    try:
        logger.info("[Flask Startup] Loading embedding and reranker models...")
        model_resources.load_models()
        logger.info("[Flask Startup] Models loaded successfully.")
    except Exception as e:
        logger.warning(f"[Flask Startup] Failed to load models: {e}")
        logger.warning("[Flask Startup] WARNING: Continuing without models for testing...")

def _initialize_services():
    """Initialize shared services during app startup."""
    try:
        logger.info("[Flask Startup] Initializing shared services...")
        service_manager.initialize()
        logger.info("[Flask Startup] Shared services initialized successfully.")
    except Exception as e:
        logger.error(f"[Flask Startup] Failed to initialize services: {e}")
        raise

def _register_routes(app):
    """Import and register application routes."""
    try:
        logger.info("[Flask Startup] Registering routes...")
        app.register_blueprint(main_bp)
        logger.info("[Flask Startup] Routes registered successfully.")

        # Debug
        logger.debug("[Flask Startup] Available routes:")
        for rule in app.url_map.iter_rules():
            logger.debug(f"  {rule.methods} {rule.rule}")
    except Exception as e:
        logger.error(f"[Flask Startup] ERROR: Failed to register routes: {e}")
        raise