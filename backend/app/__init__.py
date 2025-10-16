from flask import Flask, send_from_directory, send_file
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
import redis
import os
from datetime import datetime
try:
    from config.settings import config
except ImportError:
    from backend.config.settings import config

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
    try:
        # Try relative imports first (when running from backend directory)
        try:
            from app.blueprints.auth import auth_bp
            from app.blueprints.users import users_bp
            from app.blueprints.records import records_bp
            from app.blueprints.access import access_bp
            from app.blueprints.patients import patients_bp
            from app.blueprints.admin import admin_bp
        except ImportError:
            # Fall back to absolute imports (when running from project root)
            from backend.app.blueprints.auth import auth_bp
            from backend.app.blueprints.users import users_bp
            from backend.app.blueprints.records import records_bp
            from backend.app.blueprints.access import access_bp
            from backend.app.blueprints.patients import patients_bp
            from backend.app.blueprints.admin import admin_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(users_bp, url_prefix='/api/users')
        app.register_blueprint(records_bp, url_prefix='/api/records')
        app.register_blueprint(access_bp, url_prefix='/api/access')
        app.register_blueprint(patients_bp, url_prefix='/api/patients')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        
        print("✅ All blueprints registered successfully")
    except Exception as e:
        print(f"❌ Error registering blueprints: {e}")
        import traceback
        traceback.print_exc()
    
    # Add basic routes
    @app.route('/')
    def index():
        return {
            'message': 'Medical Records Management System API',
            'version': '1.0.1',  # Updated version to verify server restart
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users', 
                'records': '/api/records',
                'access': '/api/access',
                'patients': '/api/patients'
            }
        }
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
    
    @app.route('/debug/routes')
    def debug_routes():
        """Debug endpoint to show all registered routes"""
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        return {'routes': routes}
    
    @app.route('/api/test')
    def api_test():
        """Simple API test endpoint"""
        return {
            'message': 'API is working',
            'timestamp': datetime.utcnow().isoformat()
        }
    
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