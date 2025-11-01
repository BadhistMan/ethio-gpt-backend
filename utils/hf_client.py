import os
import requests
import logging
from typing import Dict, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class HFClient:
    def __init__(self):
        self.api_key = os.environ.get('HF_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"
        
    def _make_request(self, model: str, inputs: Any, parameters: Optional[Dict] = None):
        """Make request to Hugging Face API"""
        if not self.api_key:
            raise ValueError("Hugging Face API key not configured")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{model}"
        payload = {"inputs": inputs}
        if parameters:
            payload["parameters"] = parameters
            
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"HF API request failed: {e}")
            raise
    
    def chat_completion(self, message: str) -> str:
        """Generate chat completion using a conversational model"""
        try:
            # Using Microsoft's DialoGPT-medium for chat
            result = self._make_request(
                "microsoft/DialoGPT-medium",
                f"User: {message}\nBot:",
                {"max_length": 500, "temperature": 0.7, "do_sample": True}
            )
            
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
                # Extract only the bot's response
                if "Bot:" in generated_text:
                    return generated_text.split("Bot:")[-1].strip()
                return generated_text
            return "I apologize, but I couldn't generate a response at this time."
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            return "Sorry, I'm experiencing technical difficulties. Please try again later."
    
    def generate_image(self, prompt: str, preset: str = "realistic") -> str:
        """Generate image using Stable Diffusion"""
        try:
            # Map presets to different models
            model_map = {
                "ghibli": "22h/vintage-illustration",
                "cartoon": "ogkalu/Comic-Diffusion",
                "anime": "cagliostrolab/animagine-xl-3.1",
                "realistic": "stabilityai/stable-diffusion-xl-base-1.0"
            }
            
            model = model_map.get(preset, "stabilityai/stable-diffusion-xl-base-1.0")
            enhanced_prompt = self._enhance_prompt(prompt, preset)
            
            response = requests.post(
                f"{self.base_url}/{model}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"inputs": enhanced_prompt}
            )
            
            if response.status_code == 200:
                return self._save_temp_file(response.content, '.png')
            raise ValueError("Image generation failed")
                
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise
    
    def _enhance_prompt(self, prompt: str, preset: str) -> str:
        """Enhance prompt based on preset"""
        enhancements = {
            "ghibli": f"Studio Ghibli style, anime, beautiful, cinematic, {prompt}",
            "cartoon": f"cartoon style, vibrant colors, comic book, {prompt}",
            "anime": f"anime style, Japanese animation, detailed, {prompt}",
            "realistic": f"photorealistic, high quality, detailed, 4k, {prompt}"
        }
        return enhancements.get(preset, prompt)
    
    def _save_temp_file(self, file_data: bytes, extension: str) -> str:
        """Save file to temp directory and return filename"""
        filename = f"{uuid.uuid4()}{extension}"
        filepath = os.path.join('temp', filename)
        
        # Ensure temp directory exists
        os.makedirs('temp', exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(file_data)
            
        return filename
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = "en") -> str:
        """Translate text using HF models"""
        try:
            # Simple translation implementation
            if target_lang in ["am", "ti"]:
                # For Ethiopian languages, return placeholder text
                ethio_translations = {
                    "am": f"Amharic Translation: {text}",
                    "ti": f"Tigrinya Translation: {text}"
                }
                return ethio_translations.get(target_lang, text)
            else:
                model = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
                result = self._make_request(model, text)
                
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('translation_text', text)
                return text
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    def text_to_speech(self, text: str) -> str:
        """Convert text to speech"""
        try:
            response = requests.post(
                f"{self.base_url}/facebook/mms-tts-eng",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"inputs": text}
            )
            
            if response.status_code == 200:
                return self._save_temp_file(response.content, '.wav')
            raise ValueError("TTS failed")
            
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            raise
    
    def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text"""
        try:
            response = requests.post(
                f"{self.base_url}/facebook/wav2vec2-base-960h",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=audio_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('text', '')
            raise ValueError("STT failed")
            
        except Exception as e:
            logger.error(f"STT failed: {e}")
            raise
