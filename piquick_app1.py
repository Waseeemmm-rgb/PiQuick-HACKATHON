import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="PIQuick Dashboard - OQBI Oman", layout="wide")

# ----------------------------
# Custom CSS for Background & Colors
# ----------------------------
st.markdown("""
<style>
body, .main, .block-container {
    background-color: #fafdfd; 
    color: #293161; 
}
h1, h2, h3, h4 {
    color: #ff8000; 
    font-weight: bold;
}
.summary-card {
    background-color: #ffffffd0;
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
}
.stDataFrame thead th {
    background-color: #ffb366; 
    color: #003366;
}
input[type=number] {
    font-weight: bold;
    border-radius: 6px;
}
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #ffffff;
    border-radius: 6px;
    border: 1px solid #ccc;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Initialization and Configuration Data
# ----------------------------
if 'analyzed_days' not in st.session_state:
    st.session_state.analyzed_days = []

days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]
params = {
    "pressure": "Pressure (bar)",
    "temperature": "Temperature (°C)",
    "flow": "Flow (Kg/hour)",
    "vibration": "Vibration (Hz)",
    "oil_condition": "Oil Condition Index",
    "chemical_concentration": "Chemical Concentration (%)",
    "energy_consumption": "Energy Consumption (GJ)",
    "emissions": "Emissions (%)",
    "production_unit": "Production Unit (ton/day)"
}

limits = {
    "pressure": (20.0, 50.0),
    "temperature": (200.0, 300.0),
    "flow": (1.0, 100.0),
    "vibration": (10.0, 80.0),
    "oil_condition": (20.0, 80.0),
    "chemical_concentration": (30.0, 90.0),
    "energy_consumption": (25.0, 50.0),
    "emissions": (1.0, 30.0),
    "production_unit": (50.0, 500.0)
}

if 'params_data' not in st.session_state:
    st.session_state.params_data = {
        day: {param: (limits[param][0] + limits[param][1]) / 2 for param in params}
        for day in days
    }

# ----------------------------
# Preserve selected day across reruns
# ----------------------------
if 'selected_day_clean' not in st.session_state:
    st.session_state.selected_day_clean = days[0]  # default Day 1

# ----------------------------
# Header UI
# ----------------------------
dropdown_options = [f"{d} ✅" if d in st.session_state.analyzed_days else d for d in days]
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("<h1>🚀 <span style='color:#ff8000;'>OQBI</span> Oman - PIQuick Risk Dashboard ⚙️📊</h1>", unsafe_allow_html=True)
    st.write("Monitor industrial parameters, detect anomalies, and visualize trends easily. 🛢️💡")
with col2:
    selected_day = st.selectbox("📅 Select Day", dropdown_options, key="day_selector",
                                index=days.index(st.session_state.selected_day_clean))
st.session_state.selected_day_clean = selected_day.replace(" ✅", "")
selected_day_clean = st.session_state.selected_day_clean

# ----------------------------
# Parameter Limits Reference Table
# ----------------------------
st.markdown("<h3>Reference: Parameter Operational Ranges</h3>", unsafe_allow_html=True)
st.markdown("""
| Parameter | Unit | Lower Limit | Upper Limit |
| :--- | :--- | :--- | :--- |
| Pressure | bar | $20.0$ | $50.0$ |
| Temperature | $^{\\circ}\\text{C}$ | $200.0$ | $300.0$ |
| Flow | $\\text{Kg/hour}$ | $1.0$ | $100.0$ |
| Vibration | $\\text{Hz}$ | $10.0$ | $80.0$ |
| Oil Condition | Index | $20.0$ | $80.0$ |
| Chemical Concentration | $\\%$ | $30.0$ | $90.0$ |
| Energy Consumption | $\\text{GJ}$ | $25.0$ | $50.0$ |
| Emissions | $\\%$ | $1.0$ | $30.0$ |
| Production Unit | $\\text{ton/day}$ | $50.0$ | $500.0$ |
""")

# ----------------------------
# Input for Selected Day with ranges
# ----------------------------
st.markdown(f"<h3>📝 Enter Process Data for {selected_day_clean}</h3>", unsafe_allow_html=True)
st.divider()
cols = st.columns(3)
i = 0
for param, label in params.items():
    lower, upper = limits[param]
    display_label = f"{label} (Range: {lower} - {upper})"
    current_value = st.session_state.params_data[selected_day_clean][param]
    with cols[i % 3]:
        val = st.number_input(display_label, value=current_value, step=1.0, key=f"{param}_{selected_day_clean}", format="%.2f")
        val_float = float(val)
        is_normal = lower <= val_float <= upper
        color = "darkgreen" if is_normal else "red"
        font_weight = "bold" if not is_normal else "normal"
        status_icon = "✅ Normal Range" if is_normal else "🔥 Risk Detected"
        st.markdown(f"<p style='color:{color}; font-weight:{font_weight}; margin-top:-10px; font-size:0.9em;'>Status: {status_icon}</p>", unsafe_allow_html=True)
        st.session_state.params_data[selected_day_clean][param] = val
    i += 1
st.divider()

# ----------------------------
# Analyze and Visualize
# ----------------------------
if st.button("Analyze and Generate Report", type="primary"):
    if selected_day_clean not in st.session_state.analyzed_days:
        st.session_state.analyzed_days.append(selected_day_clean)
        st.session_state.selected_day_clean = selected_day_clean  # <-- keep current day
        st.rerun()

    df = pd.DataFrame([{ "Day": d, **st.session_state.params_data[d]} for d in days])
    
    st.subheader("📊 Full Process Data Summary")
    
    # ----------------------------
    # ✅ Highlight out-of-range values in red cells
    def highlight_out_of_range(val, param):
        lower, upper = limits[param]
        if val < lower or val > upper:
            return 'background-color: #ffcccc; font-weight: bold; color: #660000;'
        return ''
    
    styled_df = df.style.apply(lambda col: [
        highlight_out_of_range(v, col.name) if col.name in limits else '' for v in col
    ], axis=0)

    st.dataframe(styled_df, height=300, use_container_width=True)

    # ----------------------------
    # Summary
    summary_list = []
    for d in days:
        for param, label in params.items():
            lower, upper = limits[param]
            val = st.session_state.params_data[d][param]
            if val < lower:
                summary_list.append(f"⚠️ {label} (Value: {val:.2f}) is below {lower} on {d}.")
            elif val > upper:
                summary_list.append(f"🔥 {label} (Value: {val:.2f}) is above {upper} on {d}.")
    if not summary_list:
        summary_text = "✅ All parameters within normal range."
    else:
        summary_text = "\n".join(summary_list)
    st.markdown(f"<div class='summary-card'><h4>Summary of Critical Events</h4><pre>{summary_text}</pre></div>", unsafe_allow_html=True)

    # ----------------------------
    # Trend Graph for all days
    st.subheader("📈 Process Parameter Trend Analysis")
    plot_df = df.set_index("Day")
    fig, ax = plt.subplots(figsize=(12, 5))
    for param, label in params.items():
        ax.plot(plot_df.index, plot_df[param], marker="o", label=label, linewidth=2)
    ax.set_title("Process Parameter Trends Over 5 Days", fontsize=16, color="#003366")
    ax.set_xlabel("Day", fontsize=12)
    ax.set_ylabel("Value", fontsize=12)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)
