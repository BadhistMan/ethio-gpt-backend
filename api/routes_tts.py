from flask import Blueprint, request, jsonify
from flask_limiter import limiter
from utils.hf_client import HFClient

tts_bp = Blueprint('tts', __name__)
hf_client = HFClient()

@tts_bp.route('/tts', methods=['POST'])
@limiter.limit("30 per hour")
def text_to_speech():
    try:
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
@limiter.limit("30 per hour")
def speech_to_text():
    try:
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
