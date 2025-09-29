# Chatbot Configuration for Gemini API
import os
import google.generativeai as genai
from typing import Optional, Dict, Any, Tuple
import base64
from PIL import Image
import io

class ChatbotConfig:
    def __init__(self):
        # Try environment variable first
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        # If not found, try to import from config file
        if not self.api_key:
            try:
                from api_key_config import GEMINI_API_KEY
                self.api_key = GEMINI_API_KEY
            except ImportError:
                pass
        
        # If still not found, use placeholder
        if not self.api_key:
            self.api_key = "your_gemini_api_key_here"
        
        # Configure Gemini and select supported models dynamically
        genai.configure(api_key=self.api_key)
        self.text_model_name, self.vision_model_name = self._select_models()
        self.text_model = genai.GenerativeModel(self.text_model_name)
        # vision model may equal text model (if flash supports images)
        self.vision_model = genai.GenerativeModel(self.vision_model_name)
        
        # System prompt for brief Malayalam responses
        self.system_prompt = """
        നിങ്ങൾ ഒരു കാർഷിക വിദഗ്ധനാണ്. ഇനിപ്പറയുന്ന നിയമങ്ങൾ പാലിക്കുക:

        1. എല്ലായ്പ്പോഴും മലയാളത്തിൽ മാത്രം മറുപടി നൽകുക
        2. ചുരുക്കമായും കൃത്യമായും മറുപടി നൽകുക (2-3 വാക്യങ്ങൾ മാത്രം)
        3. കാർഷിക വിഷയങ്ങളിൽ മാത്രം ശ്രദ്ധ കേന്ദ്രീകരിക്കുക
        4. ചിത്രങ്ങൾ അപ്‌ലോഡ് ചെയ്താൽ, ഇല രോഗങ്ങൾ കണ്ടെത്തുകയും ചികിത്സാ നിർദ്ദേശങ്ങൾ നൽകുകയും ചെയ്യുക
        5. കൃഷി, വിളകൾ, മണ്ണ്, വളം, കീടനാശിനി, കാലാവസ്ഥ, വിപണി വിലകൾ എന്നിവയെക്കുറിച്ച് മാത്രം സംസാരിക്കുക
        6. കേരളത്തിലെ പ്രാദേശിക കൃഷി അവസ്ഥകൾ കണക്കിലെടുക്കുക
        7. ശാസ്ത്രീയമായും പ്രായോഗികമായും ഉള്ള ഉപദേശങ്ങൾ മാത്രം നൽകുക
        8. ചുരുക്കമായ ഉത്തരങ്ങൾ നൽകുക - വിശദമായ വിവരണങ്ങൾ ഒഴിവാക്കുക

        ഉദാഹരണം:
        - "എന്റെ നെല്ലിന് എന്ത് രോഗമാണ്?" → ചുരുക്കമായ രോഗ നിർണയവും ചികിത്സയും
        - "ഇന്നത്തെ കാലാവസ്ഥ എങ്ങനെയാണ്?" → കൃഷി സംബന്ധിച്ച ചോദ്യമല്ല, മറ്റ് വിഷയങ്ങളിൽ മാത്രം ശ്രദ്ധ കേന്ദ്രീകരിക്കുക
        """
    
    def _select_models(self) -> Tuple[str, str]:
        """
        Dynamically list available models and select the first one that supports generateContent.
        Returns (text_model_name, vision_model_name).
        """
        try:
            # List all available models and find ones that support generateContent
            models = genai.list_models()
            text_candidates = []
            vision_candidates = []
            
            for model in models:
                model_name = getattr(model, 'name', '')
                if not model_name:
                    continue
                    
                # Extract clean model name (remove 'models/' prefix)
                clean_name = model_name.split('/')[-1] if '/' in model_name else model_name
                
                # Check if model supports generateContent
                supported_methods = getattr(model, 'supported_generation_methods', [])
                
                if 'generateContent' in supported_methods:
                    # Prefer stable models over preview/experimental ones
                    if 'preview' not in clean_name.lower() and 'exp' not in clean_name.lower():
                        if 'vision' in clean_name.lower() or 'multimodal' in clean_name.lower():
                            vision_candidates.append(clean_name)
                        else:
                            text_candidates.append(clean_name)
            
            # Select the first stable model for each type, fallback to any available
            if not text_candidates:
                # Fallback to any model with generateContent support
                for model in models:
                    model_name = getattr(model, 'name', '')
                    if not model_name:
                        continue
                    clean_name = model_name.split('/')[-1] if '/' in model_name else model_name
                    supported_methods = getattr(model, 'supported_generation_methods', [])
                    if 'generateContent' in supported_methods and 'vision' not in clean_name.lower():
                        text_candidates.append(clean_name)
                        break
            
            text_model = text_candidates[0] if text_candidates else 'gemini-1.5-flash'
            vision_model = vision_candidates[0] if vision_candidates else text_candidates[0] if text_candidates else 'gemini-1.5-flash'
            
            return text_model, vision_model
            
        except Exception as e:
            print(f"Error listing models: {e}")
            # Fallback to safe defaults
            return 'gemini-1.5-flash', 'gemini-1.5-flash'

    def get_text_model(self):
        return self.text_model

    def get_vision_model(self):
        return self.vision_model
    
    def is_configured(self) -> bool:
        return self.api_key and self.api_key != "your_gemini_api_key_here"
    
    def get_system_prompt(self) -> str:
        return self.system_prompt
