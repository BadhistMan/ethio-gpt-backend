from flask import Blueprint, request, jsonify, send_file
from flask_limiter import limiter
import os
from utils.hf_client import HFClient

image_bp = Blueprint('image', __name__)
hf_client = HFClient()

@image_bp.route('/image', methods=['POST'])
@limiter.limit("10 per hour")
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        preset = data.get('preset', 'realistic')
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        if len(prompt) > 500:
            return jsonify({"error": "Prompt too long. Maximum 500 characters."}), 400
        
        # Generate image
        filename = hf_client.generate_image(prompt, preset)
        
        return jsonify({
            "url": f"/api/files/{filename}",
            "filename": filename
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
