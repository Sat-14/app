from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from auth import auth_bp
from bills import bills_bp
from reminders import reminders_bp
from receipts import receipts_bp
from scheduler import start_scheduler
from local_storage_service import init_storage
import os


def create_app():
    # This is the corrected version without the duplicated line.
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Set max file size for uploads
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    JWTManager(app)
    
    # Initialize local storage
    init_storage()
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(bills_bp, url_prefix='/api/bills')
    app.register_blueprint(reminders_bp, url_prefix='/api/reminders')
    app.register_blueprint(receipts_bp, url_prefix='/api/receipts')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Bills Reminder API is running'}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({'message': 'File too large. Maximum size is 16MB'}), 413
    

    return app


if __name__ == '__main__':
    app = create_app()
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # This is the final fix: Start the scheduler, then run the app with
    # use_reloader=False to ensure only a single process is running.
    start_scheduler(app)
    app.run(debug=True, port=5000, use_reloader=False)
