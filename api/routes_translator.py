from flask import Blueprint, request, jsonify
from flask_limiter import limiter
from utils.hf_client import HFClient

translator_bp = Blueprint('translator', __name__)
hf_client = HFClient()

@translator_bp.route('/translate', methods=['POST'])
@limiter.limit("50 per hour")
def translate_text():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        target_lang = data.get('target_lang', 'en')
        source_lang = data.get('source_lang', 'en')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        if len(text) > 2000:
            return jsonify({"error": "Text too long. Maximum 2000 characters."}), 400
        
        # Translate text
        translated = hf_client.translate_text(text, target_lang, source_lang)
        
        return jsonify({
            "translated_text": translated,
            "original_text": text,
            "source_lang": source_lang,
            "target_lang": target_lang
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
