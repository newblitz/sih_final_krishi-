import streamlit as st
from PIL import Image
import requests
import io
import base64
from config import HUGGINGFACE_API_KEY, MODEL_ID, API_URL, TIMEOUT_SECONDS, IMAGE_SIZE, IMAGE_QUALITY, MAX_FILE_SIZE_MB

# --- App Configuration ---
st.set_page_config(
    page_title="Crop Leaf Disease Detector",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- Configuration imported from config.py ---
# All API settings and sensitive data are now in config.py for better security

# --- Helper Functions ---

def validate_api_token(api_token):
    """
    Validates the API token format and provides helpful guidance.
    """
    if not api_token:
        return False, "No API token provided"
    
    if not api_token.startswith('hf_'):
        return False, "API token should start with 'hf_'"
    
    if len(api_token) < 20:
        return False, "API token appears to be too short"
    
    return True, "Valid token format"

def test_model_availability(api_token):
    """
    Tests if the model is available and accessible.
    """
    headers = {"Authorization": f"Bearer {api_token}"}
    try:
        # Make a simple request to check model status
        response = requests.get(f"https://api-inference.huggingface.co/models/{MODEL_ID}", headers=headers, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            return True, "Model is available"
        else:
            return False, f"Model check failed: {response.status_code}"
    except Exception as e:
        return False, f"Could not check model: {e}"

def query_api(image_bytes, api_token):
    """
    Sends an image to the Hugging Face Inference API and returns the prediction.
    """
    # Validate token first
    is_valid, message = validate_api_token(api_token)
    if not is_valid:
        st.error(f"Invalid API token: {message}")
        st.info("💡 **How to get your API token:**")
        st.markdown("""
        1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
        2. Click "New token"
        3. Give it a name (e.g., "Streamlit App")
        4. Select "Read" permissions
        5. Copy the token (it should start with 'hf_')
        """)
        return None
    
    # Convert image bytes to base64
    try:
        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        st.error(f"Failed to encode image: {e}")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Prepare the payload
    payload = {
        "inputs": img_base64
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT_SECONDS)
        
        # Check for specific status codes
        if response.status_code == 400:
            st.error("❌ **Bad Request (400)**")
            st.error("The request format is invalid. Trying alternative method...")
            
            # Try alternative method with raw bytes
            st.info("🔄 **Trying alternative request format...**")
            headers_alt = {"Authorization": f"Bearer {api_token}"}
            response_alt = requests.post(API_URL, headers=headers_alt, data=image_bytes, timeout=TIMEOUT_SECONDS)
            
            if response_alt.status_code == 200:
                st.success("✅ **Success with alternative method!**")
                return response_alt.json()
            else:
                st.error("❌ **Both methods failed**")
                st.info("💡 **Troubleshooting:**")
                st.markdown("""
                - Try uploading a different image (JPG, JPEG, or PNG)
                - Make sure the image is not corrupted
                - Ensure the image is not too large (max 10MB)
                - Try converting the image to RGB format
                """)
                # Show response details for debugging
                try:
                    error_details = response.json()
                    st.error(f"Base64 method error: {error_details}")
                except:
                    st.error(f"Base64 method response: {response.text[:200]}...")
                
                try:
                    error_details_alt = response_alt.json()
                    st.error(f"Raw bytes method error: {error_details_alt}")
                except:
                    st.error(f"Raw bytes method response: {response_alt.text[:200]}...")
                return None
        elif response.status_code == 401:
            st.error("🔐 **Authentication Error (401)**")
            st.error("Your API token is invalid or doesn't have the right permissions.")
            st.info("💡 **Troubleshooting:**")
            st.markdown("""
            - Make sure you copied the token correctly (no extra spaces)
            - Ensure the token has "Read" permissions
            - Try creating a new token if the current one doesn't work
            - The token should start with 'hf_' and be about 37 characters long
            """)
            return None
        elif response.status_code == 403:
            st.error("🚫 **Access Forbidden (403)**")
            st.error("Your API token doesn't have permission to access this model.")
            return None
        elif response.status_code == 429:
            st.error("⏳ **Rate Limit Exceeded (429)**")
            st.error("You've made too many requests. Please wait a moment and try again.")
            return None
        elif response.status_code == 503:
            st.error("🔧 **Service Unavailable (503)**")
            st.error("The model is currently loading. Please wait a moment and try again.")
            return None
        
        response.raise_for_status()  # Raise an exception for other bad status codes
        return response.json()
        
    except requests.exceptions.Timeout:
        st.error("⏱️ **Request Timeout**")
        st.error("The request took too long. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🌐 **Connection Error**")
        st.error("Could not connect to Hugging Face API. Please check your internet connection.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ **API request failed:** {e}")
        st.error("Please ensure your API token is correct and the model is available.")
        return None

def format_prediction(prediction):
    """Formats the prediction for display."""
    if not prediction:
        return "No prediction available."

    # Sort by score in descending order and take the top one
    top_result = sorted(prediction, key=lambda x: x['score'], reverse=True)[0]

    label = top_result['label'].replace("_", " ").title()
    score = top_result['score']
    return f"**{label}** (Confidence: {score:.2%})"


# --- Streamlit UI ---

st.title("🌿 Crop Leaf Disease Detector")

st.markdown("""
Welcome to the Crop Leaf Disease Detector!

**How to use:**
1.  Upload an image of a crop leaf.
2.  Click the "Classify Leaf" button to see the prediction.


""")

# --- API Token Configuration ---
# Use hardcoded API key
api_token = HUGGINGFACE_API_KEY

# --- Main App Area ---

uploaded_file = st.file_uploader("Choose a leaf image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    try:
        image = Image.open(uploaded_file)
        
        # Convert to RGB if necessary (handles RGBA, P mode images)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image to standard dimensions
        original_size = image.size
        image = image.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        st.image(image, caption=f"Uploaded Leaf Image (resized to {IMAGE_SIZE[0]}x{IMAGE_SIZE[1]})", use_column_width=True)
        
        # Show image info
        st.info(f"📸 **Original Size:** {original_size[0]}x{original_size[1]} pixels")
        st.info(f"📸 **Processed Size:** {image.size[0]}x{image.size[1]} pixels, Mode: {image.mode}")

        # Convert image to bytes with proper format
        img_byte_arr = io.BytesIO()
        # Always save as JPEG for consistency
        image.save(img_byte_arr, format='JPEG', quality=IMAGE_QUALITY)
        img_bytes = img_byte_arr.getvalue()
        
        # Show file size
        file_size_mb = len(img_bytes) / (1024 * 1024)
        st.info(f"📁 **File Size:** {file_size_mb:.2f} MB")
        
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.warning(f"⚠️ **Warning:** File size is large. Consider using a smaller image for faster processing.")

        # Classify button
        if st.button("Classify Leaf", type="primary"):
            with st.spinner("Analyzing the image..."):
                prediction = query_api(img_bytes, api_token)

            st.subheader("Prediction Result:")
            if prediction:
                result_text = format_prediction(prediction)
                st.success(result_text)
            else:
                st.error("Could not get a prediction. Please check the logs for errors.")
                    
    except Exception as e:
        st.error(f"❌ **Error processing image:** {e}")
        st.info("💡 **Try uploading a different image format (JPG, JPEG, or PNG)**")

else:
    st.info("Please upload an image to get started.")

# --- Footer Information ---
st.markdown("---")

# Create columns for footer info
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔧 Configuration")
    st.success("✅ **API Token Configured**")
    # st.info("Using secure configuration file")

# with col2:
#     # st.markdown("### 🎯 Model Info")
#     st.info(f"**Model:** {MODEL_ID}")
    
    # Model status check button
    # if st.button("🔍 Check Model Status", key="model_check"):
    #     with st.spinner("Checking model..."):
    #         is_available, message = test_model_availability(api_token)
    #         if is_available:
    #             st.success(f"✅ {message}")
    #         else:
    #             st.error(f"❌ {message}")

# with col3:
#     st.markdown("### 📊 App Status")
#     # Show token validation status
#     is_valid, message = validate_api_token(api_token)
#     if is_valid:
#         st.success("✅ Token format is valid!")
#     else:
#         st.error(f"❌ {message}")
    
    # st.info("**Image Size:** 224x224 pixels")
    # st.info("**Max File Size:** 10MB")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🌿 <strong>Crop Leaf Disease Detector</strong> 
</div>
""", unsafe_allow_html=True)