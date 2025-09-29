import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from chatbot_component import render_chatbot_sidebar

st.title("🌾 KeralaFarmAssist — Personal Farm Assistant / കേരള കൃഷി സഹായി")
st.markdown("*Smart cultivation cost estimation and budget planning for Kerala farmers*")
st.markdown("*കേരള കർഷകർക്കുള്ള സ്മാർട്ട് കൃഷി ചെലവ് കണക്കാക്കൽ, ബജറ്റ് ആസൂത്രണം*")

# Render the agricultural chatbot in sidebar
render_chatbot_sidebar()

LOCATION_DATA = {"district": "Kottayam", "season": "Kharif 2024", "soil_type": "Alluvial", "rainfall": "Heavy"}

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("District / ജില്ല", LOCATION_DATA["district"])
with col2: st.metric("Season / ഋതു", LOCATION_DATA["season"])
with col3: st.metric("Soil Type / മണ്ണിന്റെ തരം", LOCATION_DATA["soil_type"])
with col4: st.metric("Rainfall / മഴ", LOCATION_DATA["rainfall"])

COST_TEMPLATES = {
    "Rice": {
        "Conventional": {"Seeds": 2500, "Fertilizer": 4000, "Pesticides": 1200, "Labor": 6000, "Irrigation": 1500, "Other": 800, "yield_quintals": 30},
        "Organic": {"Seeds": 2800, "Fertilizer": 3200, "Pesticides": 0, "Labor": 7000, "Irrigation": 1500, "Other": 1000, "yield_quintals": 25},
        "SRI": {"Seeds": 1800, "Fertilizer": 3000, "Pesticides": 800, "Labor": 7500, "Irrigation": 1200, "Other": 700, "yield_quintals": 35}
    },
    "Coconut": {
        "Conventional": {"Seeds": 0, "Fertilizer": 3500, "Pesticides": 800, "Labor": 4000, "Irrigation": 2000, "Other": 1200, "yield_quintals": 20},
        "Organic": {"Seeds": 0, "Fertilizer": 2800, "Pesticides": 0, "Labor": 5000, "Irrigation": 2000, "Other": 1500, "yield_quintals": 18}
    },
    "Tapioca": {
        "Conventional": {"Seeds": 3000, "Fertilizer": 2500, "Pesticides": 600, "Labor": 5000, "Irrigation": 800, "Other": 600, "yield_quintals": 150},
        "Organic": {"Seeds": 3200, "Fertilizer": 2000, "Pesticides": 0, "Labor": 6000, "Irrigation": 800, "Other": 800, "yield_quintals": 130}
    },
    "Banana": {
        "Conventional": {"Seeds": 4000, "Fertilizer": 5000, "Pesticides": 1500, "Labor": 8000, "Irrigation": 2500, "Other": 1000, "yield_quintals": 200},
        "Organic": {"Seeds": 4200, "Fertilizer": 4000, "Pesticides": 0, "Labor": 9000, "Irrigation": 2500, "Other": 1300, "yield_quintals": 180}
    },
    "Vegetables": {
        "Conventional": {"Seeds": 1500, "Fertilizer": 3000, "Pesticides": 2000, "Labor": 7000, "Irrigation": 2000, "Other": 500, "yield_quintals": 80},
        "Organic": {"Seeds": 1800, "Fertilizer": 2500, "Pesticides": 0, "Labor": 8000, "Irrigation": 2000, "Other": 700, "yield_quintals": 70}
    },
    "Other": {
        "Conventional": {"Seeds": 2000, "Fertilizer": 3000, "Pesticides": 1000, "Labor": 5000, "Irrigation": 1500, "Other": 500, "yield_quintals": 50},
        "Organic": {"Seeds": 2200, "Fertilizer": 2500, "Pesticides": 0, "Labor": 6000, "Irrigation": 1500, "Other": 800, "yield_quintals": 45}
    }
}

RECOMMENDATIONS = {
    "Rice": {
        "Conventional": {"seeds": "Use certified high-yielding varieties like Jyothi, Uma, or Mahsuri", "fertilizer": "Apply NPK 20:10:10 at 150kg/acre + urea 50kg/acre", "practices": "Maintain 2-3cm water level, weed control at 20-25 days"},
        "Organic": {"seeds": "Use indigenous varieties like Palakkadan Matta or Pokkali", "fertilizer": "Use farm yard manure 2 tons/acre + neem cake 100kg/acre", "practices": "Practice crop rotation, use biological pest control"},
        "SRI": {"seeds": "Use 8-12 day old seedlings, single seedling per hill", "fertilizer": "Reduce fertilizer by 25%, use organic matter", "practices": "Maintain alternate wetting and drying, wider spacing"}
    }
}

def calculate_costs(crop, approach, area, custom_costs=None):
    base_costs = custom_costs if custom_costs else COST_TEMPLATES.get(crop, COST_TEMPLATES["Other"]).get(approach, COST_TEMPLATES["Other"]["Conventional"])
    total_costs = {k: v * area for k, v in base_costs.items() if k != "yield_quintals"}
    total_cost = sum(total_costs.values())
    yield_total = base_costs.get("yield_quintals", 50) * area
    return total_costs, total_cost, yield_total

def get_recommendations(crop, approach):
    return RECOMMENDATIONS.get(crop, {}).get(approach, {"seeds": "Consult local agricultural extension officer for seed recommendations", "fertilizer": "Soil testing recommended for optimal fertilizer application", "practices": "Follow integrated farming practices for better yield"})

st.sidebar.header("🌱 Farm Planning Inputs / കൃഷി ആസൂത്രണ ഇൻപുട്ടുകൾ")
crop = st.sidebar.selectbox("Select Crop / വിള തിരഞ്ഞെടുക്കുക", ["Rice", "Coconut", "Tapioca", "Banana", "Vegetables", "Other"], index=0)
approach = st.sidebar.selectbox("Select Farming Approach / കൃഷി രീതി തിരഞ്ഞെടുക്കുക", ["Conventional", "Organic", "SRI", "Mixed"], index=0)
area = st.sidebar.number_input("Area (in acres) / വിസ്തീർണ്ണം (ഏക്കറിൽ)", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)
market_price = st.sidebar.number_input("Market Price per Quintal (₹) - Optional / ക്വിന്റലിന് വിപണി വില (₹) - ഓപ്ഷണൽ", min_value=0, value=2000, step=100, help="Current market price for profit estimation / ലാഭ കണക്കാക്കാൻ നിലവിലെ വിപണി വില")

st.sidebar.divider()
compute_costs = st.sidebar.button("🧮 Compute Costs / ചെലവ് കണക്കാക്കുക", type="primary")
compare_approaches = st.sidebar.button("⚖️ Compare Approaches / രീതികൾ താരതമ്യം ചെയ്യുക")
export_results = st.sidebar.button("📊 Export Results / ഫലങ്ങൾ എക്സ്പോർട്ട് ചെയ്യുക")

if 'cost_data' not in st.session_state: st.session_state.cost_data = None
if 'comparison_data' not in st.session_state: st.session_state.comparison_data = None

if compute_costs:
    costs, total_cost, yield_total = calculate_costs(crop, approach, area)
    cost_per_acre = total_cost / area
    cost_per_quintal = total_cost / yield_total if yield_total > 0 else 0
    profit_per_quintal = market_price - cost_per_quintal if market_price > 0 else 0
    total_revenue = yield_total * market_price if market_price > 0 else 0
    net_profit = total_revenue - total_cost if market_price > 0 else 0
    st.session_state.cost_data = {'crop': crop, 'approach': approach, 'area': area, 'costs': costs, 'total_cost': total_cost, 'cost_per_acre': cost_per_acre, 'yield_total': yield_total, 'cost_per_quintal': cost_per_quintal, 'market_price': market_price, 'profit_per_quintal': profit_per_quintal, 'total_revenue': total_revenue, 'net_profit': net_profit}

if compare_approaches:
    comparison_data = []
    available_approaches = ["Conventional", "Organic", "SRI"] if crop in ["Rice"] else ["Conventional", "Organic"]
    for app in available_approaches:
        costs, total_cost, yield_total = calculate_costs(crop, app, area)
        cost_per_quintal = total_cost / yield_total if yield_total > 0 else 0
        profit_per_quintal = market_price - cost_per_quintal if market_price > 0 else 0
        comparison_data.append({'Approach': app, 'Total Cost (₹)': f"₹{total_cost:,.0f}", 'Expected Yield (Quintals)': f"{yield_total:.1f}", 'Cost per Quintal (₹)': f"₹{cost_per_quintal:.0f}", 'Profit per Quintal (₹)': f"₹{profit_per_quintal:.0f}" if market_price > 0 else "N/A"})
    st.session_state.comparison_data = comparison_data

if st.session_state.cost_data:
    data = st.session_state.cost_data
    st.header("📊 Quick Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Cost", f"₹{data['total_cost']:,.0f}")
    with col2: st.metric("Cost per Acre", f"₹{data['cost_per_acre']:,.0f}")
    with col3: st.metric("Expected Yield", f"{data['yield_total']:.1f} quintals")
    with col4:
        if data['market_price'] > 0: st.metric("Net Profit", f"₹{data['net_profit']:,.0f}")
        else: st.metric("Cost per Quintal", f"₹{data['cost_per_quintal']:,.0f}")
    st.divider()
    st.header("💰 Detailed Cost Breakdown")
    cost_df = pd.DataFrame(list(data['costs'].items()), columns=['Cost Type', 'Amount'])
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.pie(cost_df, values='Amount', names='Cost Type', title=f"Cost Distribution for {data['crop']} ({data['approach']} approach)")
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Cost Details")
        for cost_type, amount in data['costs'].items(): st.write(f"**{cost_type}:** ₹{amount:,.0f}")
        st.write(f"**Total:** ₹{data['total_cost']:,.0f}")
    st.divider()

if st.session_state.comparison_data:
    st.header("⚖️ Approach Comparison")
    comparison_df = pd.DataFrame(st.session_state.comparison_data)
    st.dataframe(comparison_df, use_container_width=True)
    if market_price > 0:
        chart_data = []
        for app in (["Conventional", "Organic", "SRI"] if crop == "Rice" else ["Conventional", "Organic"]):
            costs, total_cost, yield_total = calculate_costs(crop, app, area)
            cost_per_quintal = total_cost / yield_total if yield_total > 0 else 0
            profit_per_quintal = market_price - cost_per_quintal if market_price > 0 else 0
            chart_data.append({'Approach': app, 'Total Cost': total_cost, 'Expected Yield': yield_total, 'Profit per Quintal': profit_per_quintal})
        chart_df = pd.DataFrame(chart_data)
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(chart_df, x='Approach', y='Total Cost', title="Total Cost Comparison", color='Approach')
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.bar(chart_df, x='Approach', y='Profit per Quintal', title="Profit per Quintal Comparison", color='Approach')
            st.plotly_chart(fig2, use_container_width=True)
    st.divider()

if st.session_state.cost_data:
    data = st.session_state.cost_data
    st.header("📅 Budget Planner")
    phases = {"Land Preparation": {"Seeds": 1.0, "Labor": 0.2, "Other": 0.3}, "Sowing/Planting": {"Seeds": 0.0, "Labor": 0.2, "Other": 0.2}, "Growth Phase": {"Fertilizer": 0.6, "Pesticides": 0.5, "Irrigation": 0.5, "Labor": 0.3}, "Mid Season": {"Fertilizer": 0.4, "Pesticides": 0.5, "Irrigation": 0.3, "Labor": 0.2}, "Harvest": {"Irrigation": 0.2, "Labor": 0.3, "Other": 0.5}}
    budget_data = []
    for phase, ratios in phases.items():
        phase_cost = 0
        for cost_type, ratio in ratios.items():
            if cost_type in data['costs']: phase_cost += data['costs'][cost_type] * ratio
        budget_data.append({"Phase": phase, "Cost (₹)": f"₹{phase_cost:,.0f}", "Amount": phase_cost})
    budget_df = pd.DataFrame(budget_data)
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(budget_df, x='Phase', y='Amount', title="Phase-wise Cost Distribution", color='Phase')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Budget Schedule")
        for _, row in budget_df.iterrows(): st.write(f"**{row['Phase']}:** {row['Cost (₹)']}")
    st.divider()

if st.session_state.cost_data:
    data = st.session_state.cost_data
    st.header("🌱 Recommendations")
    recommendations = get_recommendations(data['crop'], data['approach'])
    col1, col2, col3 = st.columns(3)
    with col1: st.subheader("🌾 Seeds"); st.info(recommendations.get('seeds', 'No specific recommendations available'))
    with col2: st.subheader("🌿 Fertilizer"); st.info(recommendations.get('fertilizer', 'No specific recommendations available'))
    with col3: st.subheader("🚜 Practices"); st.info(recommendations.get('practices', 'No specific recommendations available'))
    st.subheader("💡 General Tips")
    tips = [f"For {data['crop']} cultivation, maintain proper spacing between plants", f"Monitor weather conditions regularly during {LOCATION_DATA['season']}", f"In {LOCATION_DATA['district']}, consider local variety preferences", "Regular soil testing helps optimize fertilizer usage", "Implement integrated pest management for sustainable farming"]
    for tip in tips: st.write(f"• {tip}")

def create_export_data():
    if not st.session_state.cost_data: return None, None
    data = st.session_state.cost_data
    csv_data = {'Farm Details': [f"Crop: {data['crop']}", f"Approach: {data['approach']}", f"Area: {data['area']} acres", f"Season: {LOCATION_DATA['season']}", f"District: {LOCATION_DATA['district']}", "", "Cost Breakdown:"]}
    for cost_type, amount in data['costs'].items(): csv_data['Farm Details'].append(f"{cost_type}: ₹{amount:,.0f}")
    csv_data['Farm Details'].extend(["", f"Total Cost: ₹{data['total_cost']:,.0f}", f"Cost per Acre: ₹{data['cost_per_acre']:,.0f}", f"Expected Yield: {data['yield_total']:.1f} quintals", f"Cost per Quintal: ₹{data['cost_per_quintal']:,.0f}"])
    if data['market_price'] > 0: csv_data['Farm Details'].extend([f"Market Price: ₹{data['market_price']:,.0f}/quintal", f"Total Revenue: ₹{data['total_revenue']:,.0f}", f"Net Profit: ₹{data['net_profit']:,.0f}"])
    csv_df = pd.DataFrame(csv_data)
    csv_buffer = pd.io.common.BytesIO()
    csv_df.to_csv(csv_buffer, index=False)
    csv_data_bytes = csv_buffer.getvalue()
    return csv_data_bytes, csv_df

if export_results:
    if st.session_state.cost_data:
        csv_data, csv_df = create_export_data()
        if csv_data:
            st.success("✅ Export data prepared successfully!")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(label="📄 Download CSV Report", data=csv_data, file_name=f"farm_report_{crop}_{approach}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", type="primary")
            with col2:
                st.subheader("📋 Report Preview")
                st.dataframe(csv_df, use_container_width=True)
    else:
        st.warning("⚠️ Please compute costs first before exporting results.")

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🌾 <strong>KeralaFarmAssist</strong> - Empowering Kerala farmers with data-driven cultivation insights</p>
    <p><em>Built for Smart India Hackathon | Made with ❤️ for farmers</em></p>
</div>
""", unsafe_allow_html=True)



