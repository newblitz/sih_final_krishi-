import streamlit as st
from PIL import Image
import requests
import io
import base64
from sih.sih.config import HUGGINGFACE_API_KEY, MODEL_ID, API_URL, TIMEOUT_SECONDS, IMAGE_SIZE, IMAGE_QUALITY, MAX_FILE_SIZE_MB
from chatbot_component import AgriculturalChatbot

st.title("🌿 Crop Leaf Disease Detector / ഇല രോഗ കണ്ടെത്തൽ")

def validate_api_token(api_token):
    if not api_token:
        return False, "No API token provided"
    if not api_token.startswith('hf_'):
        return False, "API token should start with 'hf_'"
    if len(api_token) < 20:
        return False, "API token appears to be too short"
    return True, "Valid token format"

def test_model_availability(api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    try:
        response = requests.get(f"https://api-inference.huggingface.co/models/{MODEL_ID}", headers=headers, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            return True, "Model is available"
        else:
            return False, f"Model check failed: {response.status_code}"
    except Exception as e:
        return False, f"Could not check model: {e}"

def query_api(image_bytes, api_token):
    is_valid, message = validate_api_token(api_token)
    if not is_valid:
        st.error(f"Invalid API token: {message}")
        st.info("💡 How to get your API token:")
        st.markdown("""
        1. Go to https://huggingface.co/settings/tokens
        2. Create a token with Read permissions
        3. Copy the token (starts with 'hf_')
        """)
        return None

    try:
        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        st.error(f"Failed to encode image: {e}")
        return None

    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    payload = {"inputs": img_base64}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT_SECONDS)
        if response.status_code == 400:
            st.error("Bad Request (400)")
            headers_alt = {"Authorization": f"Bearer {api_token}"}
            response_alt = requests.post(API_URL, headers=headers_alt, data=image_bytes, timeout=TIMEOUT_SECONDS)
            if response_alt.status_code == 200:
                return response_alt.json()
            return None
        elif response.status_code in (401, 403, 429, 503):
            st.error(f"API Error: {response.status_code}")
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None

def format_prediction(prediction):
    if not prediction:
        return "No prediction available."
    top_result = sorted(prediction, key=lambda x: x['score'], reverse=True)[0]
    label = top_result['label'].replace("_", " ").title()
    score = top_result['score']
    return f"**{label}** (Confidence: {score:.2%})"

api_token = HUGGINGFACE_API_KEY

uploaded_file = st.file_uploader("Choose a leaf image... / ഒരു ഇല ചിത്രം തിരഞ്ഞെടുക്കുക...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        original_size = image.size
        image = image.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
        st.image(image, caption=f"Uploaded Leaf Image (resized to {IMAGE_SIZE[0]}x{IMAGE_SIZE[1]}) / അപ്‌ലോഡ് ചെയ്ത ഇല ചിത്രം ({IMAGE_SIZE[0]}x{IMAGE_SIZE[1]} ആയി വലുപ്പം മാറ്റി)", use_column_width=True)
        st.info(f"Original Size: {original_size[0]}x{original_size[1]} pixels / യഥാർത്ഥ വലുപ്പം: {original_size[0]}x{original_size[1]} പിക്സൽ")
        st.info(f"Processed Size: {image.size[0]}x{image.size[1]} pixels, Mode: {image.mode} / പ്രോസസ് ചെയ്ത വലുപ്പം: {image.size[0]}x{image.size[1]} പിക്സൽ, മോഡ്: {image.mode}")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=IMAGE_QUALITY)
        img_bytes = img_byte_arr.getvalue()
        file_size_mb = len(img_bytes) / (1024 * 1024)
        st.info(f"File Size: {file_size_mb:.2f} MB / ഫയൽ വലുപ്പം: {file_size_mb:.2f} MB")
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.warning("File is large. Consider using a smaller image. / ഫയൽ വലുതാണ്. ചെറിയ ചിത്രം ഉപയോഗിക്കുക.")
        if st.button("Classify Leaf / ഇല വർഗീകരിക്കുക", type="primary"):
            with st.spinner("Analyzing the image... / ചിത്രം വിശകലനം ചെയ്യുന്നു..."):
                prediction = query_api(img_bytes, api_token)
            st.subheader("Prediction Result: / പ്രവചന ഫലം:")
            if prediction:
                result_text = format_prediction(prediction)
                st.success(result_text)
                
                # Extract disease name for treatment advice
                top_result = sorted(prediction, key=lambda x: x['score'], reverse=True)[0]
                disease_name = top_result['label'].replace("_", " ").title()
                
                # Get treatment advice from chatbot
                st.markdown("---")
                st.subheader("Treatment Advice / ചികിത്സാ ഉപദേശം")
                
                if 'chatbot' not in st.session_state:
                    st.session_state.chatbot = AgriculturalChatbot()
                
                chatbot = st.session_state.chatbot
                if chatbot.is_configured():
                    with st.spinner("Getting treatment advice... / ചികിത്സാ ഉപദേശം നേടുന്നു..."):
                        treatment_query = f"{disease_name} രോഗത്തിനുള്ള ചികിത്സ എന്താണ്? ജൈവവും രാസവുമായ ഓപ്ഷനുകൾ ഉൾപ്പെടെ ചുരുക്കമായ ചികിത്സാ നിർദ്ദേശങ്ങൾ നൽകുക."
                        treatment_advice = chatbot.process_text_query(treatment_query)
                        st.markdown(treatment_advice)
                else:
                    st.warning("Chatbot not configured. Please set GEMINI_API_KEY environment variable.")
                
                # Add report button
                st.markdown("---")
                if st.button("📋 Get Full Report", type="secondary"):
                    st.info("Full report feature coming soon!")
            else:
                st.error("Could not get a prediction. / പ്രവചനം നേടാൻ കഴിഞ്ഞില്ല.")
    except Exception as e:
        st.error(f"Error processing image: {e} / ചിത്രം പ്രോസസ് ചെയ്യുമ്പോൾ പിശക്: {e}")
else:
    st.info("Please upload an image to get started. / ആരംഭിക്കാൻ ഒരു ചിത്രം അപ്‌ലോഡ് ചെയ്യുക.")



