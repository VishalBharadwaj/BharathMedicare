from flask import Flask, send_from_directory, send_file
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
import redis
import os
from datetime import datetime
from config.settings import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    jwt = JWTManager(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize database connections
    app.mongo_client = MongoClient(app.config['MONGODB_URI'])
    app.db = app.mongo_client[app.config['MONGODB_DB']]
    app.redis_client = redis.from_url(app.config['REDIS_URL'])
    
    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.users import users_bp
    from app.blueprints.records import records_bp
    from app.blueprints.access import access_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(records_bp, url_prefix='/api/records')
    app.register_blueprint(access_bp, url_prefix='/api/access')
    
    # Add basic routes
    @app.route('/')
    def index():
        return {
            'message': 'Medical Records Management System API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users', 
                'records': '/api/records',
                'access': '/api/access'
            }
        }
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
    
    # Serve frontend static files
    @app.route('/<path:filename>')
    def serve_frontend(filename):
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
        return send_from_directory(frontend_dir, filename)
    
    @app.route('/pages/<path:filename>')
    def serve_pages(filename):
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'pages')
        return send_from_directory(frontend_dir, filename)
    
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'assets')
        return send_from_directory(frontend_dir, filename)
    
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'js')
        return send_from_directory(frontend_dir, filename)
    
    return app