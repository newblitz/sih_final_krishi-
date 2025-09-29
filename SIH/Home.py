import streamlit as st
from chatbot_component import render_chatbot_sidebar

st.set_page_config(page_title="Agri Suite", page_icon="🧑‍🌾", layout="wide", initial_sidebar_state="expanded")

st.title("🧑‍🌾 Agri Suite / കാർഷിക സ്യൂട്ട്")
st.markdown("*Unified dashboards: Disease Detection, Farm Planning, Weather Advisory, and Agri Market*")
st.markdown("*ഏകീകൃത ഡാഷ്ബോർഡുകൾ: രോഗ കണ്ടെത്തൽ, കൃഷി ആസൂത്രണം, കാലാവസ്ഥാ ഉപദേശം, കാർഷിക വിപണി*")

st.markdown("---")

st.header("📚 Available Dashboards / ലഭ്യമായ ഡാഷ്ബോർഡുകൾ")
st.markdown(
    """
    - **🌿 Crop Leaf Disease Detector / ഇല രോഗ കണ്ടെത്തൽ**: Classify diseases from leaf images using a ViT model.
    - **🌾 KeralaFarmAssist / കേരള കൃഷി സഹായി**: Plan cultivation costs, compare approaches, and export reports.
    - **☀️ Krishi Sakhi (Weather Advisory) / കൃഷി സഖി**: Stage-aware advisories with Malayalam support based on local forecast.
    - **🏪 Agri Market / കാർഷിക വിപണി**: Agriculture market analysis and trading platform.
    """
)

# Use the sidebar to navigate to any dashboard page

# Render the agricultural chatbot in sidebar
render_chatbot_sidebar()

# Handle redirect from other pages
if st.session_state.get('redirect_to_chatbot', False):
    st.session_state.redirect_to_chatbot = False



