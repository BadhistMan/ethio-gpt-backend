from flask import Blueprint, request, jsonify
from flask_limiter import limiter
from utils.hf_client import HFClient

chat_bp = Blueprint('chat', __name__)
hf_client = HFClient()

@chat_bp.route('/chat', methods=['POST'])
@limiter.limit("20 per hour")
def chat():
    try:
        data = request.get_json()
        user_input = data.get('input', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_input:
            return jsonify({"error": "Input is required"}), 400
        
        if len(user_input) > 1000:
            return jsonify({"error": "Input too long. Maximum 1000 characters."}), 400
        
        # Generate response
        response = hf_client.chat_completion(user_input)
        
        return jsonify({
            "reply": response,
            "meta": {"model": "microsoft/DialoGPT-medium", "session_id": session_id}
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
