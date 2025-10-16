#!/usr/bin/env python3
"""
Medical Records Management System - Main Application Entry Point
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path for proper imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from flask import Flask
from app import create_app
from app.models.database import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Get configuration environment
    config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask application
    app = create_app(config_name)
    
    # Initialize database manager
    db_manager.init_app(app)
    
    # Log startup information
    logger.info(f"Starting Medical Records System in {config_name} mode")
    logger.info(f"Database: {app.config['MONGODB_URI']}")
    logger.info(f"Redis: {app.config['REDIS_URL']}")
    
    # Run the application
    if config_name == 'development':
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
            # ssl_context='adhoc'  # Disabled HTTPS for easier development
        )
    else:
        # Production should use a proper WSGI server like Gunicorn
        logger.info("Use a production WSGI server like Gunicorn for production deployment")
        app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()