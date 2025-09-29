# 🤖 Agricultural Chatbot Integration

## Overview

This Streamlit app now includes a powerful AI-powered agricultural assistant powered by Google's Gemini API. The chatbot is accessible across all pages and provides:

- **Malayalam-only responses** for agricultural questions
- **Image analysis** for crop disease detection
- **Smart filtering** to only answer agriculture-related questions
- **Cross-page availability** on all dashboard pages

## Features

### 🌾 Agricultural Focus
- Only responds to questions about farming, crops, soil, fertilizers, weather, market prices
- Automatically filters out non-agricultural questions
- Provides expert advice on cultivation practices

### 🖼️ Image Analysis
- Upload crop/leaf images for disease detection
- Get detailed disease identification and treatment recommendations
- Receive prevention tips and management strategies

### 🗣️ Malayalam Interface
- All responses are in Malayalam
- Understands both Malayalam and English questions
- Culturally relevant advice for Kerala farmers

### 🔄 Cross-Page Integration
- Available on all pages: Home, Weather Advisory, Disease Detector, Farm Assist, Agri Market
- Consistent experience across the entire application
- Chat history maintained during session

## Files Added/Modified

### New Files:
- `chatbot_config.py` - Gemini API configuration
- `chatbot_component.py` - Main chatbot component
- `GEMINI_SETUP.md` - API setup guide
- `test_chatbot.py` - Test script
- `CHATBOT_README.md` - This documentation

### Modified Files:
- `Home.py` - Added chatbot integration
- `pages/0_☀️Weather_Advisory.py` - Added chatbot integration
- `pages/1_🌿_Leaf_Disease_Detector.py` - Added chatbot integration
- `pages/2_🌾_KeralaFarmAssist.py` - Added chatbot integration
- `pages/4_🏪Agri_Market.py` - Added chatbot integration
- `requirements.txt` - Added Gemini API dependency

## Setup Instructions

### 1. Get Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the generated key

### 2. Set Environment Variable
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Test the Integration
```bash
python test_chatbot.py
```

### 5. Run the App
```bash
streamlit run Home.py
```

## Usage

### Text Queries
1. Navigate to any page in the app
2. Look for "🤖 കാർഷിക സഹായി" in the sidebar
3. Type your agricultural question in the text area
4. Click "💬 ചോദിക്കുക" to get a response

### Image Analysis
1. Upload a crop/leaf image using the file uploader
2. Optionally add a specific question about the image
3. Click "💬 ചോദിക്കുക" for disease analysis

### Example Questions
- "എന്റെ നെല്ലിന് എന്ത് രോഗമാണ്?"
- "വിളവ് എങ്ങനെ വർദ്ധിപ്പിക്കാം?"
- "ഏത് വളം ഉപയോഗിക്കണം?"
- "കാലാവസ്ഥ അനുസരിച്ച് എന്ത് ചെയ്യണം?"

## Technical Details

### Architecture
- **Config**: `chatbot_config.py` handles API configuration
- **Component**: `chatbot_component.py` provides the main chatbot logic
- **Integration**: Each page imports and renders the chatbot component

### Key Functions
- `AgriculturalChatbot.process_text_query()` - Handle text questions
- `AgriculturalChatbot.process_image_query()` - Analyze uploaded images
- `AgriculturalChatbot.is_agricultural_question()` - Filter non-agricultural questions
- `render_chatbot_sidebar()` - Render the chatbot UI

### Error Handling
- Graceful handling of missing API keys
- Clear error messages in Malayalam
- Fallback responses for API failures

## Troubleshooting

### Common Issues
1. **"API കീ ക്രമീകരിച്ചിട്ടില്ല"** - Set GEMINI_API_KEY environment variable
2. **Import errors** - Run `pip install -r requirements.txt`
3. **Non-agricultural responses** - The chatbot is designed to only answer farming-related questions

### Testing
Run the test script to verify everything works:
```bash
python test_chatbot.py
```

## Future Enhancements

- Voice input support
- Multi-language support (English responses option)
- Integration with local agricultural databases
- Real-time market price integration
- Weather-based recommendations

## Support

For issues or questions:
1. Check the setup guide in `GEMINI_SETUP.md`
2. Run the test script to verify configuration
3. Ensure all dependencies are installed correctly
