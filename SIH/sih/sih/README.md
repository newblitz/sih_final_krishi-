# Crop Leaf Disease Detection Streamlit App

This is a simple web application built with Streamlit that uses a pre-trained Vision Transformer (ViT) model from Hugging Face to classify diseases in crop leaves.

## Features
- Upload an image of a crop leaf (.jpg, .jpeg, .png)
- Get a classification of the leaf's condition from the Hugging Face model
- Simple and intuitive user interface
- Secure API key configuration

## How to Run

### 1. Prerequisites
- Python 3.7+
- A Hugging Face account and a User Access Token with "read" permissions

### 2. Setup Configuration
1. Copy `config_template.py` to `config.py`
2. Edit `config.py` and replace `"your_huggingface_api_key_here"` with your actual Hugging Face API token
3. Get your API token from [Hugging Face Settings](https://huggingface.co/settings/tokens)

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit App
```bash
streamlit run app.py
```

### 5. Use the App
1. Your web browser should open a new tab with the Streamlit application
2. Use the file uploader to select an image of a crop leaf from your computer
3. Click the "Classify Leaf" button
4. The application will display the predicted disease or condition with its confidence score

## Security Notes
- The `config.py` file contains your API key and is excluded from version control
- Never share your `config.py` file or commit it to a repository
- The `config_template.py` file is safe to share and commit

## Model Used
- **Model**: wambugu71/crop_leaf_diseases_vit
- **Type**: Vision Transformer (ViT)
- **Purpose**: Crop leaf disease classification