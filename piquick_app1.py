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
    background-color: #d0e7f9;
    color: #003366;
}
h1, h2, h3, h4 {
    color: #ffb366;
    font-weight: bold;
}
.summary-card {
    background-color: #ffffffb3;
    padding: 15px;
    border-radius: 10px;
    margin-top: 10px;
}
.stDataFrame thead th {
    background-color: #ffb366;
    color: #003366;
}
.day-selector {
    position: absolute;
    top: 20px;
    right: 30px;
}
input[type=number] {
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Header with dropdown
# ----------------------------
# Track analyzed days in session_state
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

# Limits
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

# Track parameter values in session_state
if 'params_data' not in st.session_state:
    st.session_state.params_data = {day: {param: (limits[param][0]+limits[param][1])/2 for param in params} for day in days}

# Create dropdown with tick marks for analyzed days
dropdown_options = []
for d in days:
    if d in st.session_state.analyzed_days:
        dropdown_options.append(f"{d} ✅")
    else:
        dropdown_options.append(d)

col1, col2 = st.columns([5,1])
with col1:
    st.markdown("<h1 style='text-align:center;'><span style='color:#ff8000; font-weight:bold;'>OQBI Oman</span> - PIQuick Risk Dashboard</h1>", unsafe_allow_html=True)
with col2:
    selected_day = st.selectbox("📅 Select Day", dropdown_options, key="day_selector")

# Normalize selected_day to remove tick if exists
selected_day_clean = selected_day.replace(" ✅","")

st.write("Monitor industrial parameters, detect anomalies, and visualize trends easily.")

# ----------------------------
# Input for Selected Day
# ----------------------------
st.markdown(f"<h3>📝 Enter Process Data for {selected_day_clean}</h3>", unsafe_allow_html=True)
cols = st.columns(3)
i = 0
for param, label in params.items():
    lower, upper = limits[param]
    with cols[i % 3]:
        val = st.number_input(f"{label} ({selected_day_clean})", 
                              value=st.session_state.params_data[selected_day_clean][param], 
                              step=1.0,
                              key=f"{param}_{selected_day_clean}")
        color = "green" if lower <= val <= upper else "red"
        st.markdown(f"<p style='color:{color}; font-weight:bold;'>Value: {val}</p>", unsafe_allow_html=True)
        st.session_state.params_data[selected_day_clean][param] = val
    i += 1

# ----------------------------
# Risk Classification
# ----------------------------
def classify_risk(value, param):
    lower, upper = limits[param]
    if value < lower:
        return "Low"
    elif value > upper:
        return "High"
    else:
        return "Normal"

if st.button("Analyze Data"):
    # Mark day as analyzed
    if selected_day_clean not in st.session_state.analyzed_days:
        st.session_state.analyzed_days.append(selected_day_clean)

    # Combine all days into DataFrame
    df = pd.DataFrame([{ "Day": d, **st.session_state.params_data[d]} for d in days ])

    # Add risk columns
    for param in params.keys():
        df[param + "_risk"] = df[param].apply(lambda x: classify_risk(x, param))

    # Styled table for risk
    def color_risk(val):
        if val == "High":
            color = "red"
        elif val == "Low":
            color = "orange"
        else:
            color = "green"
        return f"background-color:{color}; color:white; font-weight:bold; text-align:center;"

    st.subheader("📊 Process Data & Risk Levels")
    styled_df = df.style.map(color_risk, subset=[p + "_risk" for p in params.keys()])
    st.dataframe(styled_df, height=500)

    # ----------------------------
    # Summary
    summary = ""
    for param in params.keys():
        high_days = df[df[param+"_risk"]=="High"]["Day"].tolist()
        low_days = df[df[param+"_risk"]=="Low"]["Day"].tolist()
        if high_days:
            summary += f"🔥 {param.replace('_',' ').title()} High: {', '.join(high_days)}\n"
        if low_days:
            summary += f"⚠️ {param.replace('_',' ').title()} Low: {', '.join(low_days)}\n"
    if not summary:
        summary = "✅ All parameters within normal range."

    st.markdown(f"""
    <div class='summary-card'>
    <h4>Summary of Critical Events</h4>
    <pre>{summary}</pre>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------
    # Trend Graph for all days
    fig, ax = plt.subplots(figsize=(12, 6))
    for param in params.keys():
        ax.plot(df["Day"], df[param], marker="o", label=params[param], linewidth=2)
    ax.set_title("Process Parameter Trends", fontsize=16, color="#ffb366")
    ax.set_xlabel("Day")
    ax.set_ylabel("Value")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    st.pyplot(fig)
