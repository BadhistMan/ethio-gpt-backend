from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import uuid
import time

# Simple in-memory user store (replace with database in production)
users_db = {}
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        display_name = data.get('display_name', '').strip()
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        
        if username in users_db:
            return jsonify({"error": "Username already exists"}), 400
        
        # Create new user
        user_id = str(uuid.uuid4())
        users_db[username] = {
            'id': user_id,
            'username': username,
            'display_name': display_name or username,
            'created_at': time.time(),
            'usage_count': 0
        }
        
        # Create access token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            "access_token": access_token,
            "user": {
                "id": user_id,
                "username": username,
                "display_name": display_name or username
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        user = users_db.get(username)
        if not user:
            # Auto-register if user doesn't exist
            return register()
        
        # Create access token
        access_token = create_access_token(identity=user['id'])
        
        return jsonify({
            "access_token": access_token,
            "user": {
                "id": user['id'],
                "username': user['username'],
                "display_name": user['display_name']
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/me')
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        
        # Find user by ID
        user = next((u for u in users_db.values() if u['id'] == user_id), None)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": {
                "id": user['id'],
                "username": user['username'],
                "display_name": user['display_name'],
                "usage_count": user['usage_count']
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
