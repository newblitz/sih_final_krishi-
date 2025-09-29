import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import os
from chatbot_component import render_chatbot_sidebar

st.title("☀️ Weather Advisory")

BASE_URL = "https://api.open-meteo.com/v1/forecast"

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CALENDAR_FILE = os.path.join(PROJECT_ROOT, "sih4", "crop_calendars_kerala_ml.csv")

KERALA_DISTRICTS = {
    "Thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366},
    "Kollam": {"lat": 8.8932, "lon": 76.6141},
    "Pathanamthitta": {"lat": 9.2662, "lon": 76.7870},
    "Alappuzha": {"lat": 9.4981, "lon": 76.3388},
    "Kottayam": {"lat": 9.5916, "lon": 76.5222},
    "Idukki": {"lat": 9.8560, "lon": 77.1094},
    "Ernakulam": {"lat": 9.9816, "lon": 76.2999},
    "Thrissur": {"lat": 10.5276, "lon": 76.2144},
    "Palakkad": {"lat": 10.7867, "lon": 76.6548},
    "Malappuram": {"lat": 11.0510, "lon": 76.0711},
    "Kozhikode": {"lat": 11.2588, "lon": 75.7804},
    "Wayanad": {"lat": 11.6854, "lon": 76.1320},
    "Kannur": {"lat": 11.8745, "lon": 75.3704},
    "Kasaragod": {"lat": 12.4996, "lon": 74.9869},
}

@st.cache_data(ttl=1800)
def get_weather_data(lat: float, lon: float) -> Optional[Dict]:
    params = {"latitude": lat, "longitude": lon, "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code", "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,soil_temperature_0_to_7cm", "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_gusts_10m_max", "timezone": "auto", "forecast_days": 7}
    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Weather API Error: {e}")
        return None

@st.cache_data
def load_crop_calendars() -> pd.DataFrame:
    try:
        df = pd.read_csv(CALENDAR_FILE)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{CALENDAR_FILE}' was not found. Ensure it exists.")
        return pd.DataFrame()

class CropLifecycleAdvisor:
    def __init__(self, crop_calendars: pd.DataFrame):
        self.calendars = crop_calendars
    def get_stage_alerts(self, crop: str, planting_date: date, weather_data: Dict) -> List[Dict]:
        plant_age = (datetime.now().date() - planting_date).days
        crop_stages = self.calendars[self.calendars['crop'] == crop]
        triggered_alerts = []
        for _, rule in crop_stages.iterrows():
            if rule['start_day'] <= plant_age <= rule['end_day']:
                alert = self._check_weather_rule(rule, weather_data)
                if alert: triggered_alerts.append(alert)
        status = self._get_current_status(crop, plant_age)
        if status: triggered_alerts.insert(0, status)
        return triggered_alerts
    def _get_current_status(self, crop: str, plant_age: int):
        crop_stages = self.calendars[self.calendars['crop'] == crop]
        for _, row in crop_stages.iterrows():
            if row['start_day'] <= plant_age <= row['end_day']:
                concerns_ml_text = row.get('concerns_actions_ml', row['concerns_actions'])
                return {"type": "status", "plant_age": plant_age, "stage_name": row['stage_name'], "concerns_en": row['concerns_actions'].split(',')[0].strip(), "concerns_ml": concerns_ml_text.split(',')[0].strip()}
        return None
    def _check_weather_rule(self, rule: pd.Series, weather_data: Dict):
        daily_forecast = pd.DataFrame(weather_data['daily']).head(3)
        hourly_forecast = pd.DataFrame(weather_data['hourly']).head(72)
        alert_variable = rule.get('alert_variable')
        if pd.isna(alert_variable): return None
        threshold = rule['alert_threshold']
        operator = rule['alert_operator']
        forecast_value = None
        if alert_variable in daily_forecast.columns:
            forecast_value = daily_forecast[alert_variable].max() if operator == '>' else daily_forecast[alert_variable].min()
        elif alert_variable in hourly_forecast.columns:
            forecast_value = hourly_forecast[alert_variable].max() if operator == '>' else hourly_forecast[alert_variable].min()
        if forecast_value is None: return None
        triggered = (operator == '>' and forecast_value > threshold) or (operator == '<' and forecast_value < threshold)
        if triggered:
            concerns_ml_text = rule.get('concerns_actions_ml', rule['concerns_actions'])
            return {"type": "alert", "priority": rule['priority'], "concerns_en": rule['concerns_actions'], "concerns_ml": concerns_ml_text, "details": f"Forecast for '{alert_variable.replace('_',' ').title()}' is {forecast_value:.1f}, crossing the '{operator}{threshold}' threshold.", "reference_url": rule['reference_url']}
        return None

def get_weather_icon(weather_code: int) -> str:
    if weather_code in [0, 1]: return '☀️'
    if weather_code in [2, 3]: return '☁️'
    if weather_code in [45, 48]: return '🌫️'
    if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return '🌧️'
    if weather_code in [71, 73, 75, 85, 86]: return '❄️'
    if weather_code in [95, 96, 99]: return '⛈️'
    return '🌤️'

def get_malayalam_weather(weather_code: int) -> str:
    if weather_code in [0, 1]: return 'തെളിഞ്ഞ ആകാശം'
    if weather_code in [2, 3]: return 'മേഘാവൃതം'
    if weather_code in [45, 48]: return 'മൂടൽമഞ്ഞ്'
    if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return 'മഴ'
    if weather_code in [71, 73, 75, 85, 86]: return 'മഞ്ഞ്'
    if weather_code in [95, 96, 99]: return 'ഇടിമിന്നൽ'
    return 'മിതമായ കാലാവസ്ഥ'

def display_stage_aware_alerts(alerts: List[Dict]):
    st.header("💡 Stage-Aware Alerts / ഘട്ടം തിരിച്ചുള്ള മുന്നറിയിപ്പുകൾ")
    status_card = next((a for a in alerts if a['type'] == 'status'), None)
    alert_cards = [a for a in alerts if a['type'] == 'alert']
    if status_card:
        col1, col2 = st.columns(2)
        col1.metric("Plant Age / പ്രായം", f"{status_card['plant_age']} days")
        col2.metric("Current Stage / നിലവിലെ ഘട്ടം", status_card['stage_name'])
        st.info(f"**Focus for this stage:** {status_card['concerns_en']}\n\n**ശ്രദ്ധിക്കേണ്ട കാര്യങ്ങൾ:** {status_card['concerns_ml']}", icon="🎯")
    if not alert_cards:
        st.success("No critical weather threats detected for the current crop stage in the next 3 days.\n\nഅടുത്ത 3 ദിവസത്തേക്ക് നിലവിലെ വിള ഘട്ടത്തിൽ നിർണായകമായ കാലാവസ്ഥാ ഭീഷണികളൊന്നും കണ്ടെത്തിയിട്ടില്ല.", icon="✅")
        return
    for alert in sorted(alert_cards, key=lambda x: ['High', 'Medium', 'Low'].index(x['priority'])):
        message_en = f"**{alert['priority']} Priority:** {alert['concerns_en']}"
        message_ml = f"**മലയാളം:** {alert['concerns_ml']}"
        details = f"\n\n*Details: {alert['details']}*\n\n[Read More]({alert['reference_url']})"
        full_message = f"{message_en}\n\n{message_ml}{details}"
        if alert['priority'] == 'High': st.error(full_message, icon="🚨")
        elif alert['priority'] == 'Medium': st.warning(full_message, icon="⚠️")
        else: st.info(full_message, icon="ℹ️")

def display_current_weather(current_data: Dict):
    st.header("🌡️ Current Weather / നിലവിലെ കാലാവസ്ഥ")
    icon = get_weather_icon(current_data.get('weather_code', 0))
    malayalam_desc = get_malayalam_weather(current_data.get('weather_code', 0))
    st.markdown(f"""<div class="weather-card"> <div style="font-size: 4rem;">{icon}</div> <h2>{malayalam_desc}</h2> <div class="temp-display">{current_data['temperature_2m']}°C</div> <p>Feels like {current_data['apparent_temperature']}°C</p> <div class="weather-details"> <div class="detail-item"> <span class="detail-value">💧 {current_data['relative_humidity_2m']}%</span> <div class="detail-label">Humidity / ആർദ്രത</div> </div> <div class="detail-item"> <span class="detail-value">💨 {current_data['wind_speed_10m']} km/h</span> <div class="detail-label">Wind / കാറ്റ്</div> </div> <div class="detail-item"> <span class="detail-value">🌧️ {current_data['precipitation']} mm</span> <div class="detail-label">Rain / മഴ</div> </div> </div> </div>""", unsafe_allow_html=True)

def display_forecast(daily_data: pd.DataFrame):
    st.header("📅 7-Day Forecast / 7 ദിവസത്തെ പ്രവചനം")
    cols = st.columns(len(daily_data))
    for i, day in daily_data.iterrows():
        with cols[i]:
            st.markdown(f"""<div class="forecast-card"> <div class="forecast-date">{day['time'].strftime('%a')}</div> <div style="font-size: 2rem;">{get_weather_icon(day['weather_code'])}</div> <div class="forecast-temp"> <span style="color: #e74c3c;">{day['temperature_2m_max']:.0f}°</span> / <span style="color: #3498db;">{day['temperature_2m_min']:.0f}°</span> </div> <div class="forecast-details"> <div>🌧️ {day['precipitation_sum']:.1f}mm</div> </div> </div>""", unsafe_allow_html=True)

st.markdown("""
<style>
.weather-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 20px; color: white; text-align: center; margin: 1rem 0; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
.temp-display { font-size: 4rem; font-weight: bold; margin: 1rem 0; }
.weather-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
.detail-item { background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; }
.detail-value { font-size: 1.5rem; font-weight: bold; display: block; }
.forecast-card { background: white; border: 2px solid #e1e5e9; border-radius: 15px; padding: 1rem; text-align: center; height: 100%; }
.forecast-date { font-weight: bold; color: #2c3e50; }
.forecast-temp { font-size: 1.2rem; font-weight: bold; margin: 0.5rem 0; }
.forecast-details { font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# Render the agricultural chatbot in sidebar
render_chatbot_sidebar()

crop_calendars = load_crop_calendars()
if not crop_calendars.empty:
    st.sidebar.header("Your Farm Profile / നിങ്ങളുടെ ഫാം പ്രൊഫൈൽ")
    unique_crops = crop_calendars['crop'].unique()
    selected_crop = st.sidebar.selectbox("Select Your Crop / വിള തിരഞ്ഞെടുക്കുക", options=unique_crops)
    max_days = int(crop_calendars[crop_calendars['crop'] == selected_crop]['end_day'].max())
    planting_date = st.sidebar.date_input("Select Planting Date / നട്ട തീയതി തിരഞ്ഞെടുക്കുക", value=date.today() - timedelta(days=60), min_value=date.today() - timedelta(days=max_days), max_value=date.today())
    selected_district = st.sidebar.selectbox("Select Your District / ജില്ല തിരഞ്ഞെടുക്കുക", options=list(KERALA_DISTRICTS.keys()))
    st.info(f"Advisory for a **{selected_crop}** crop planted on **{planting_date.strftime('%d %B %Y')}** in **{selected_district}**.", icon="🌱")
    st.markdown("---")
    coords = KERALA_DISTRICTS[selected_district]
    with st.spinner(f"Fetching forecast and generating stage-aware alerts for {selected_district}..."):
        weather_data = get_weather_data(coords['lat'], coords['lon'])
        if weather_data:
            advisor = CropLifecycleAdvisor(crop_calendars)
            stage_alerts = advisor.get_stage_alerts(selected_crop, planting_date, weather_data)
            display_stage_aware_alerts(stage_alerts)
            st.markdown("---")
            display_current_weather(weather_data['current'])
            st.markdown("---")
            daily_df = pd.DataFrame(weather_data['daily'])
            daily_df['time'] = pd.to_datetime(daily_df['time'])
            display_forecast(daily_df)
            st.markdown("---")
            st.markdown(f"""<div style="text-align: center; padding: 2rem; margin-top: 2rem; background: #f8f9fa; border-radius: 15px; color: #6c757d;"><h4>🚨 Emergency Contacts / അടിയന്തര ബന്ധങ്ങൾ</h4><p><strong>Agriculture Dept:</strong> 1800-425-1551 | <strong>Weather Emergency:</strong> 1077</p><p><em>Data from Open-Meteo | Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</em></p></div>""", unsafe_allow_html=True)
        else:
            st.error("Could not fetch weather data. Please try again later.")



