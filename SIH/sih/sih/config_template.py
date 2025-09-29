# Configuration template for the Crop Leaf Disease Detector
# Copy this file to config.py and add your actual API key

# Hugging Face API Configuration
HUGGINGFACE_API_KEY = "your_huggingface_api_key_here"  # Replace with your actual API key
MODEL_ID = "wambugu71/crop_leaf_diseases_vit"

# API Settings
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
TIMEOUT_SECONDS = 30

# Image Processing Settings
IMAGE_SIZE = (224, 224)  # Standard size for vision models
IMAGE_QUALITY = 95  # JPEG quality (1-100)
MAX_FILE_SIZE_MB = 10
