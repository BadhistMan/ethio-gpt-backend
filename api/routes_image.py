from flask import Blueprint, request, jsonify, send_file
import os
from utils.hf_client import HFClient

image_bp = Blueprint('image', __name__)
hf_client = HFClient()

@image_bp.route('/image', methods=['POST'])
def generate_image():
    try:
        from flask import current_app
        # Apply rate limit manually
        with current_app.app_context():
            if not current_app.limiter.test_limit(image_bp.name + "image"):
                return jsonify({"error": "Rate limit exceeded"}), 429

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

@image_bp.route('/files/<filename>')
def get_image(filename):
    try:
        # Security: Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename:
            return jsonify({"error": "Invalid filename"}), 400
            
        filepath = os.path.join('temp', filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "Image not found"}), 404
            
        return send_file(filepath, mimetype='image/png')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
