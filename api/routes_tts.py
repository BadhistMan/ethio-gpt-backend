from flask import Blueprint, request, jsonify
import os
from utils.hf_client import HFClient

tts_bp = Blueprint('tts', __name__)
hf_client = HFClient()

@tts_bp.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        from flask import current_app
        # Apply rate limit manually
        with current_app.app_context():
            if not current_app.limiter.test_limit(tts_bp.name + "tts"):
                return jsonify({"error": "Rate limit exceeded"}), 429

        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        if len(text) > 1000:
            return jsonify({"error": "Text too long. Maximum 1000 characters."}), 400
        
        # Generate speech
        filename = hf_client.text_to_speech(text)
        
        return jsonify({
            "url": f"/api/files/{filename}",
            "filename": filename
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tts_bp.route('/stt', methods=['POST'])
def speech_to_text():
    try:
        from flask import current_app
        # Apply rate limit manually
        with current_app.app_context():
            if not current_app.limiter.test_limit(tts_bp.name + "stt"):
                return jsonify({"error": "Rate limit exceeded"}), 429

        if 'audio' not in request.files:
            return jsonify({"error": "Audio file is required"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No audio file selected"}), 400
        
        # Convert speech to text
        audio_data = audio_file.read()
        text = hf_client.speech_to_text(audio_data)
        
        return jsonify({"text": text})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tts_bp.route('/files/<filename>')
def get_tts(filename):
    try:
        if '..' in filename or '/' in filename:
            return jsonify({"error": "Invalid filename"}), 400
            
        filepath = os.path.join('temp', filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "Audio file not found"}), 404
            
        return send_file(filepath, mimetype='audio/wav')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
