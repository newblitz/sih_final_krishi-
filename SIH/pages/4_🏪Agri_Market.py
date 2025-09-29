import streamlit as st
import os
import sys
import runpy
from chatbot_component import render_chatbot_sidebar

st.title("🏪 Agri Market / കാർഷിക വിപണി")

# Render the agricultural chatbot in sidebar
render_chatbot_sidebar()

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Try common entry script names under SIH2 folder
CANDIDATE_FILES = [
    os.path.join(PROJECT_ROOT, "SIH2", "app.py"),
    os.path.join(PROJECT_ROOT, "SIH2", "main.py"),
    os.path.join(PROJECT_ROOT, "SIH2", "streamlit_app.py"),
    os.path.join(PROJECT_ROOT, "SIH2", "SIH2", "app.py"),
    os.path.join(PROJECT_ROOT, "SIH2", "SIH2", "main.py"),
]

entry = next((p for p in CANDIDATE_FILES if os.path.exists(p)), None)

if not entry:
    st.error("Could not find a Streamlit entry script in the SIH2 folder. / SIH2 ഫോൾഡറിൽ സ്ട്രീംലിറ്റ് എൻട്രി സ്ക്രിപ്റ്റ് കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
else:
    # Change working directory so relative paths inside SIH2 work
    cwd = os.getcwd()
    entry_dir = os.path.dirname(entry)
    try:
        os.chdir(entry_dir)
        # Ensure local module imports like 'data_fetcher' resolve
        if entry_dir not in sys.path:
            sys.path.insert(0, entry_dir)
        # Inform the embedded app not to call st.set_page_config again
        os.environ["EMBEDDED_STREAMLIT"] = "1"
        # Execute the found script in this process
        runpy.run_path(entry, run_name="__main__")
    finally:
        # Best-effort removal to avoid polluting sys.path across reruns
        try:
            if entry_dir in sys.path:
                sys.path.remove(entry_dir)
        except Exception:
            pass
        # Clean the flag
        try:
            if os.environ.get("EMBEDDED_STREAMLIT"):
                del os.environ["EMBEDDED_STREAMLIT"]
        except Exception:
            pass
        os.chdir(cwd)



