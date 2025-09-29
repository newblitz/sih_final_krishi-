# Gemini API Setup Guide

## Getting Your Gemini API Key

1. **Visit Google AI Studio**: Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

2. **Sign in**: Use your Google account to sign in

3. **Create API Key**: Click "Create API Key" and copy the generated key

4. **Set Environment Variable**: Set the API key as an environment variable:

### On macOS/Linux:
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

### On Windows:
```cmd
set GEMINI_API_KEY=your_actual_api_key_here
```

### For Streamlit Cloud:
Add the environment variable in your Streamlit Cloud dashboard under "Settings" → "Environment variables"

## Running the App

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set API Key** (if not already set):
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

3. **Run Streamlit**:
```bash
streamlit run Home.py
```

## Features

- **Malayalam Responses**: All chatbot responses are in Malayalam
- **Agricultural Focus**: Only answers questions related to agriculture, farming, crops, etc.
- **Image Analysis**: Upload crop/leaf images for disease detection and treatment advice
- **Cross-Page Access**: Available on all pages of the Streamlit app
- **Smart Filtering**: Automatically filters out non-agricultural questions

## Usage

1. Navigate to any page in the app
2. Look for the "🤖 കാർഷിക സഹായി / Agricultural Assistant" section in the sidebar
3. Type your agricultural question in Malayalam or English
4. Upload crop/leaf images for disease analysis
5. Get detailed responses with treatment recommendations

## Troubleshooting

- **API Key Error**: Make sure GEMINI_API_KEY is set correctly
- **Import Error**: Ensure all dependencies are installed with `pip install -r requirements.txt`
- **Language Issues**: The chatbot is configured to respond only in Malayalam for agricultural topics
