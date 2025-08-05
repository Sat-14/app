from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, ReminderSettings
import bcrypt
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove all non-digit characters for validation
    digits_only = re.sub(r'\D', '', phone)
    # Check if it has at least 10 digits
    return len(digits_only) >= 10

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate request data
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Validate required fields
        required = ['email', 'password', 'name', 'phone_number']
        missing_fields = [field for field in required if field not in data or not data[field]]
        if missing_fields:
            return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate password length
        if len(data['password']) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
        # Validate phone number
        if not validate_phone(data['phone_number']):
            return jsonify({'message': 'Invalid phone number format'}), 400
        
        # Check if user exists
        existing_user = User.query.filter_by(email=data['email'].lower()).first()
        if existing_user:
            return jsonify({'message': 'Email already registered'}), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user = User(
            email=data['email'].lower(),  # Store email in lowercase
            password_hash=password_hash.decode('utf-8'),
            name=data['name'].strip(),
            phone_number=data['phone_number'].strip()
        )
        
        # Add user to session and flush to get the ID
        db.session.add(user)
        db.session.flush()  # This assigns the ID without committing
        
        # Create default reminder settings with the user ID
        reminder_settings = ReminderSettings(user_id=user.id)
        db.session.add(reminder_settings)
        
        # Commit both user and reminder settings
        db.session.commit()
        
        # Create token
        token = create_access_token(identity=user.id)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'phone_number': user.phone_number
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")  # Log the error for debugging
        return jsonify({'message': 'An error occurred during registration'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate request data
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password required'}), 400
        
        # Find user by email (case-insensitive)
        user = User.query.filter_by(email=data['email'].lower()).first()
        
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Check password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Create token
        token = create_access_token(identity=user.id)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'phone_number': user.phone_number
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")  # Log the error for debugging
        return jsonify({'message': 'An error occurred during login'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'phone_number': user.phone_number,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }), 200
        
    except Exception as e:
        print(f"Get profile error: {str(e)}")
        return jsonify({'message': 'An error occurred while fetching profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update name if provided
        if 'name' in data and data['name']:
            user.name = data['name'].strip()
        
        # Update phone number if provided
        if 'phone_number' in data and data['phone_number']:
            if not validate_phone(data['phone_number']):
                return jsonify({'message': 'Invalid phone number format'}), 400
            user.phone_number = data['phone_number'].strip()
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'phone_number': user.phone_number
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update profile error: {str(e)}")
        return jsonify({'message': 'An error occurred while updating profile'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # JWT tokens are stateless, so we just return success
    # In a production app, you might want to implement a token blacklist
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """Endpoint to verify if a token is still valid"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Invalid token'}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'phone_number': user.phone_number
            }
        }), 200
        
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return jsonify({'message': 'Invalid token'}), 401