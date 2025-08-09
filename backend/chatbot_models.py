# chatbot_models.py - Database models for chatbot functionality

from models import db, User
from datetime import datetime
import uuid
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ChatSession(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    ai_provider = db.Column(db.String(50), default='gemini')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='chat_sessions')

class ChatMessage(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('chat_session.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'user', 'assistant', 'system'
    content = db.Column(db.Text, nullable=False)
    function_call = db.Column(db.Text)
    function_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    session = db.relationship('ChatSession', backref='messages')

class ChatPreferences(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, unique=True)
    preferred_ai = db.Column(db.String(50), default='gemini')
    language = db.Column(db.String(10), default='en-US')
    enable_voice = db.Column(db.Boolean, default=False)
    auto_suggestions = db.Column(db.Boolean, default=True)
    gemini_api_key = db.Column(db.Text)
    openai_api_key = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='chat_preferences', uselist=False)