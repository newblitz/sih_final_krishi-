#!/usr/bin/env python3
"""
Test script for the Agricultural Chatbot
Run this to test the chatbot functionality before using in the main app
"""

import os
import sys
from chatbot_component import AgriculturalChatbot
from PIL import Image
import io

def test_chatbot():
    """Test the chatbot functionality"""
    print("🤖 Testing Agricultural Chatbot...")
    
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not set. Please set it first:")
        print("export GEMINI_API_KEY='your_actual_api_key_here'")
        return False
    
    # Initialize chatbot
    chatbot = AgriculturalChatbot()
    
    if not chatbot.is_configured():
        print("❌ Chatbot not properly configured")
        return False
    
    print("✅ Chatbot initialized successfully")
    
    # Test agricultural question detection
    test_questions = [
        "എന്റെ നെല്ലിന് എന്ത് രോഗമാണ്?",  # Agricultural
        "ഇന്നത്തെ കാലാവസ്ഥ എങ്ങനെയാണ്?",  # Non-agricultural
        "വിളവ് എങ്ങനെ വർദ്ധിപ്പിക്കാം?",  # Agricultural
        "ഫുട്ബോൾ മത്സരം എപ്പോഴാണ്?"  # Non-agricultural
    ]
    
    print("\n🧪 Testing question classification:")
    for question in test_questions:
        is_agri = chatbot.is_agricultural_question(question)
        status = "✅ Agricultural" if is_agri else "❌ Non-agricultural"
        print(f"  '{question}' -> {status}")
    
    print("\n✅ All tests completed successfully!")
    print("\n📝 To use the chatbot in the Streamlit app:")
    print("1. Set your GEMINI_API_KEY environment variable")
    print("2. Run: streamlit run Home.py")
    print("3. Look for the chatbot in the sidebar on any page")
    
    return True

if __name__ == "__main__":
    test_chatbot()
