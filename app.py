from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging
from datetime import timedelta
import json

# Import route blueprints
from api.routes_chat import chat_bp
from api.routes_image import image_bp
from api.routes_tts import tts_bp
from api.routes_translator import translator_bp
from api.routes_writer import writer_bp
from api.routes_auth import auth_bp
from api.routes_admin import admin_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Initialize extensions
    CORS(app, origins=[
        "http://localhost:3000",
        "https://*.vercel.app"
    ])
    
    jwt = JWTManager(app)
    
    # Rate limiting - CORRECT initialization
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )
    
    # Store limiter in app context for manual rate limiting
    app.limiter = limiter
    
    # Register blueprints
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(image_bp, url_prefix='/api')
    app.register_blueprint(tts_bp, url_prefix='/api')
    app.register_blueprint(translator_bp, url_prefix='/api')
    app.register_blueprint(writer_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        return jsonify({"status": "healthy", "service": "Ethio GPT Tools Backend"})
    
    # Serve uploaded files
    @app.route('/api/files/<filename>')
    def serve_file(filename):
        try:
            return send_file(f'temp/{filename}')
        except Exception as e:
            return jsonify({"error": "File not found"}), 404
    
    # Error handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({"error": "Rate limit exceeded", "message": "Too many requests"}), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('temp', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
