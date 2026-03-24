# SIH Final Krishi

Agri-focused multi-page Streamlit application built for Smart India Hackathon.  
The project combines multiple farmer tools in one interface, with bilingual support (English + Malayalam), including weather advisory, crop disease detection, farm planning, market insights, and an AI chatbot assistant.

## Project Overview

This app provides a single dashboard (`Agri Suite`) with the following modules:

- `Weather Advisory`: Kerala district-wise weather forecast and stage-aware crop alerts.
- `Crop Leaf Disease Detector`: Upload leaf images and classify likely crop diseases using a Hugging Face vision model.
- `KeralaFarmAssist`: Cultivation cost estimation, approach comparison, budget planning, and exportable reports.
- `Agri Market`: Embedded market analysis/trading page from the `SIH2` module.
- `Agricultural Chatbot`: Gemini-powered assistant integrated in the sidebar across pages.

## Tech Stack

- Python 3.10+ (recommended)
- Streamlit
- Pandas, Plotly, Requests, Pillow
- Google Gemini API (`google-generativeai`)
- Hugging Face Inference API (for leaf disease detection)

## Repository Structure

- `SIH/Home.py` - Main Streamlit app entrypoint
- `SIH/pages/` - Streamlit multipage modules
- `SIH/chatbot_component.py` - Shared chatbot component
- `SIH/chatbot_config.py` - Gemini model setup
- `SIH/sih/sih/config_template.py` - Hugging Face config template
- `SIH/SIH2/SIH2/` - Embedded Agri Market sub-app
- `SIH/requirements.txt` - Python dependencies

## Setup and Run

### 1) Clone and enter the project

```bash
git clone <your-repo-url>
cd sih_final_krishi-/SIH
```

### 2) Create and activate a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure API keys

#### Gemini (chatbot)

Set environment variable:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

On Windows:

```cmd
set GEMINI_API_KEY=your_gemini_api_key_here
```

#### Hugging Face (leaf disease detector)

1. Copy `SIH/sih/sih/config_template.py` to `SIH/sih/sih/config.py`
2. Set your key in `HUGGINGFACE_API_KEY`:

```python
HUGGINGFACE_API_KEY = "your_hf_token_here"
```

> Keep API keys private and avoid committing them to git.

### 5) Run the application

From the `SIH` directory:

```bash
streamlit run Home.py
```

Open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Optional Checks

Run chatbot test script:

```bash
python test_chatbot.py
```

## Notes

- `Agri Market` page dynamically loads the Streamlit app inside `SIH2`.
- Weather data is fetched from Open-Meteo API.
- The app is designed for Kerala agriculture scenarios and includes Malayalam content for accessibility.
