import streamlit as st
import google.generativeai as genai
from chatbot_config import ChatbotConfig
from typing import Optional, Dict, Any
import base64
from PIL import Image
import io

class AgriculturalChatbot:
    def __init__(self):
        self.config = ChatbotConfig()
        self.text_model = self.config.get_text_model()
        self.vision_model = self.config.get_vision_model()
        
    def is_configured(self) -> bool:
        return self.config.is_configured()
    
    def process_text_query(self, user_input: str) -> str:
        """Process text-based queries - let the model decide how to respond"""
        if not self.is_configured():
            return "Sorry, Gemini API key is not configured. Please set GEMINI_API_KEY environment variable."
        
        try:
            # Combine system prompt with user input
            full_prompt = f"{self.config.get_system_prompt()}\n\nUser: {user_input}\n\nExpert:"
            
            response = self.text_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error occurred: {str(e)}"
    
    def process_image_query(self, image: Image.Image, user_question: str = "") -> str:
        """Process image-based queries for analysis (disabled - text only)"""
        return "Image analysis is not available. Please ask text-based questions about agriculture."
    
    def is_agricultural_question(self, question: str) -> bool:
        """Always return True - let the model decide how to respond to any input"""
        return True

def render_chatbot_right():
    """Render the chatbot as a clean floating widget in bottom right corner"""
    # Get the current page name for unique keys
    import inspect
    import os
    try:
        frame = inspect.currentframe()
        caller_file = frame.f_back.f_globals.get('__file__', 'unknown')
        page_name = os.path.basename(caller_file).replace('.py', '').replace('_', '')
    finally:
        del frame
    
    # Set current page for chatbot state management
    st.session_state.current_page = page_name
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = AgriculturalChatbot()
    chatbot = st.session_state.chatbot

    if not chatbot.is_configured():
        return

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Custom CSS for floating widget
    st.markdown("""
    <style>
    .floating-chatbot {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        max-height: 500px;
        background: #f8f9fa;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        border: 1px solid #dee2e6;
        z-index: 1000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .chatbot-header {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 12px 12px 0 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-weight: 600;
        font-size: 14px;
    }
    
    .chatbot-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        border-radius: 50%;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 16px rgba(40, 167, 69, 0.4);
        z-index: 1001;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .chatbot-toggle:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.6);
    }
    
    .chatbot-content {
        padding: 16px;
        max-height: 400px;
        overflow-y: auto;
        background: #ffffff;
    }
    
    .chat-message {
        margin: 8px 0;
        padding: 10px 14px;
        border-radius: 18px;
        max-width: 80%;
        word-wrap: break-word;
        color: #212529;
        font-size: 14px;
        line-height: 1.4;
    }
    
    .user-message {
        background: #e9ecef;
        margin-left: auto;
        text-align: right;
        color: #212529;
    }
    
    .bot-message {
        background: #d1ecf1;
        margin-right: auto;
        color: #212529;
    }
    
    .chat-input-container {
        padding: 12px 16px;
        border-top: 1px solid #dee2e6;
        background: #f8f9fa;
    }
    
    .chat-input {
        width: 100%;
        padding: 10px 14px;
        border: 1px solid #ced4da;
        border-radius: 20px;
        outline: none;
        font-size: 14px;
        color: #212529;
        background: #ffffff;
    }
    
    .chat-input:focus {
        border-color: #28a745;
        box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
    }
    
    .send-button {
        background: #28a745;
        color: white;
        border: none;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        cursor: pointer;
        margin-left: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Toggle chatbot visibility
    if f'chatbot_open_{page_name}' not in st.session_state:
        st.session_state[f'chatbot_open_{page_name}'] = False

    # Floating toggle button
    if st.button("Ask AI", key=f"chatbot_toggle_{page_name}"):
        st.session_state[f'chatbot_open_{page_name}'] = not st.session_state[f'chatbot_open_{page_name}']
        st.rerun()

    # Show chatbot widget when open
    if st.session_state[f'chatbot_open_{page_name}']:
        st.markdown("""
        <div class="floating-chatbot">
            <div class="chatbot-header">
                <span>🤖 AI Assistant</span>
                <button onclick="this.parentElement.parentElement.style.display='none'" style="background:none;border:none;color:white;cursor:pointer;">✕</button>
            </div>
            <div class="chatbot-content" id="chat-content">
        """, unsafe_allow_html=True)

        # Display chat history
        if st.session_state.chat_history:
            for user_msg, bot_msg in st.session_state.chat_history[-3:]:  # Show last 3 messages
                st.markdown(f"""
                <div class="chat-message user-message">{user_msg}</div>
                <div class="chat-message bot-message">{bot_msg}</div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Input area
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input(
                "",
                placeholder="Ask about agriculture...",
                key=f"chatbot_input_{page_name}",
                label_visibility="collapsed"
            )
        with col2:
            send_clicked = st.button("→", key=f"chatbot_send_{page_name}")

        st.markdown("""
        </div>
        """, unsafe_allow_html=True)

        # Handle input
        if send_clicked and user_input:
            with st.spinner("Thinking..."):
                response = chatbot.process_text_query(user_input)
                st.session_state.chat_history.append((user_input, response))
            st.rerun()

        # Check for redirect from other pages
        if st.session_state.get('redirect_to_chatbot', False):
            st.session_state.redirect_to_chatbot = False
            st.session_state[f'chatbot_open_{page_name}'] = True
            st.rerun()

def render_chatbot_sidebar():
    """Render the chatbot in the sidebar (legacy function for compatibility)"""
    render_chatbot_right()