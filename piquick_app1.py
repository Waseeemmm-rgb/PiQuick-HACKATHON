import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(
    page_title="PIQuick Dashboard - OQBI Oman",
    layout="wide",
)

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
}
.summary-card {
    background-color: #ffffff90;
    padding: 15px;
    border-radius: 10px;
    margin-top: 10px;
}
.stDataFrame thead th {
    background-color: #ffb366;
    color: #003366;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Header
# ----------------------------
st.markdown("<h1 style='text-align:center;'>OQBI Oman - PIQuick Risk Dashboard</h1>", unsafe_allow_html=True)
st.write("Monitor industrial parameters, detect anomalies, and visualize trends easily.")

# ----------------------------
# Input Section
# ----------------------------
st.markdown("<h3>📝 Input Daily Process Data (5 Days)</h3>", unsafe_allow_html=True)

days = 5

pressure = []
temperature = []
flow = []
vibration = []
oil_condition = []
chemical_concentration = []
energy_consumption = []
emissions = []
production_unit = []

# Parameter limits
limits = {
    "pressure": (20.0, 50.0),
    "temperature": (200.0, 300.0),
    "flow": (1.0, 100.0),
    "vibration": (10.0, 80.0),
    "oil_condition": (20.0, 80.0),
    "chemical_concentration": (30.0, 90.0),
    "energy_consumption": (25.0, 50.0),
    "emissions": (1.0, 100.0),
    "production_unit": (50.0, 500.0)
}

for i in range(days):
    st.markdown(f"<h4>Day {i+1}</h4>", unsafe_allow_html=True)
    pressure.append(st.number_input(f"Pressure (bar) - Day {i+1}", value=35.0, step=1.0, min_value=0.0, max_value=100.0))
    temperature.append(st.number_input(f"Temperature (°C) - Day {i+1}", value=250.0, step=1.0, min_value=0.0, max_value=500.0))
    flow.append(st.number_input(f"Flow (Kg/hour) - Day {i+1}", value=50.0, step=1.0, min_value=0.0, max_value=200.0))
    vibration.append(st.number_input(f"Vibration (Hz) - Day {i+1}", value=40.0, step=1.0, min_value=0.0, max_value=200.0))
    oil_condition.append(st.number_input(f"Oil Condition Index - Day {i+1}", value=50.0, step=1.0, min_value=0.0, max_value=100.0))
    chemical_concentration.append(st.number_input(f"Chemical Concentration (%) - Day {i+1}", value=60.0, step=1.0, min_value=0.0, max_value=100.0))
    energy_consumption.append(st.number_input(f"Energy Consumption (GJ) - Day {i+1}", value=35.0, step=1.0, min_value=0.0, max_value=100.0))
    emissions.append(st.number_input(f"Emissions (ppm) - Day {i+1}", value=50.0, step=1.0, min_value=0.0, max_value=200.0))
    production_unit.append(st.number_input(f"Production Unit (ton/day) - Day {i+1}", value=250.0, step=1.0, min_value=0.0, max_value=1000.0))

# ----------------------------
# System Health Illustration
# ----------------------------
st.markdown("<h3>💡 System Health Status</h3>", unsafe_allow_html=True)

def get_system_health(value, param):
    lower, upper = limits[param]
    if value < lower:
        return "⚠️ Low"
    elif value > upper:
        return "🔥 High"
    else:
        return "✅ Normal"

for i in range(days):
    st.markdown(f"<b>Day {i+1} Status:</b>", unsafe_allow_html=True)
    st.write(f"Pressure: {get_system_health(pressure[i],'pressure')}, "
             f"Temperature: {get_system_health(temperature[i],'temperature')}, "
             f"Flow: {get_system_health(flow[i],'flow')}, "
             f"Vibration: {get_system_health(vibration[i],'vibration')}, "
             f"Oil Condition: {get_system_health(oil_condition[i],'oil_condition')}, "
             f"Chemical Conc.: {get_system_health(chemical_concentration[i],'chemical_concentration')}, "
             f"Energy: {get_system_health(energy_consumption[i],'energy_consumption')}, "
             f"Emissions: {get_system_health(emissions[i],'emissions')}, "
             f"Production: {get_system_health(production_unit[i],'production_unit')}")

# ----------------------------
# Risk Classification
# ----------------------------
def classify_risk(val, param):
    lower, upper = limits[param]
    if val < lower:
        return "Low"
    elif val > upper:
        return "High"
    else:
        return "Normal"

if st.button("Analyze Data"):
    df = pd.DataFrame({
        "Day": [f"Day {i+1}" for i in range(days)],
        "Pressure": pressure,
        "Temperature": temperature,
        "Flow": flow,
        "Vibration": vibration,
        "Oil Condition": oil_condition,
        "Chemical Concentration": chemical_concentration,
        "Energy Consumption": energy_consumption,
        "Emissions": emissions,
        "Production Unit": production_unit
    })

    # Apply risk classification for each parameter
    for param in limits.keys():
        df[param + " Risk"] = df[param].apply(lambda x: classify_risk(x, param))

    st.subheader("📊 Process Data & Risk Levels")
    st.dataframe(df, height=400)

    # Summary of high/low risk days
    summary = ""
    for param in limits.keys():
        high_days = df[df[param + " Risk"]=="High"]['Day'].tolist()
        low_days = df[df[param + " Risk"]=="Low"]['Day'].tolist()
        if high_days:
            summary += f"🔥 {param} High: {', '.join(high_days)}\n"
        if low_days:
            summary += f"⚠️ {param} Low: {', '.join(low_days)}\n"
    if summary == "":
        summary = "✅ All readings normal"

    st.markdown(f"""
    <div class='summary-card'>
        <h4>Summary of Critical Events</h4>
        <pre>{summary}</pre>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------
    # Trend Chart
    # ----------------------------
    fig, ax = plt.subplots(figsize=(12,6))
    for param in ["Pressure","Temperature","Flow","Vibration","Oil Condition",
                  "Chemical Concentration","Energy Consumption","Emissions","Production Unit"]:
        ax.plot(df['Day'], df[param], marker='o', label=param, linewidth=2)
    ax.set_title("Process Parameter Trends", fontsize=16, color='#ffb366')
    ax.set_xlabel("Day")
    ax.set_ylabel("Value")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    st.pyplot(fig)
