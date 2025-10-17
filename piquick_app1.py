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
/* Set light blue background */
body, .main, .block-container {
    background-color: #d0e7f9;
    color: #003366;
}

/* Heading color - light orange */
h1, h2, h3, h4 {
    color: #ffb366;
}

/* Card style for summary */
.summary-card {
    background-color: #ffffff90;
    padding: 15px;
    border-radius: 10px;
    margin-top: 10px;
}

/* Table header */
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

# Parameter ranges
param_ranges = {
    "Pressure": (20, 50),  # bar
    "Temperature": (200, 300),  # Celsius
    "Flow": (1, 100),  # Kg/hour
    "Vibration": (10, 80),  # Hz
    "Oil Condition": (20, 80),  # Index
    "Chemical Concentration": (30, 90),  # %
    "Energy Consumption": (25, 50),  # GJ
    "Emissions": (1, 100),  # ppm
    "Production Unit": (50, 500)  # ton/day
}

for i in range(days):
    st.markdown(f"<h4>Day {i+1}</h4>", unsafe_allow_html=True)
    pressure.append(st.number_input(f"Pressure (bar) - Day {i+1}", value=35.0, step=1, min_value=0.0, max_value=100.0))
    temperature.append(st.number_input(f"Temperature (°C) - Day {i+1}", value=250.0, step=1, min_value=0.0, max_value=500.0))
    flow.append(st.number_input(f"Flow (Kg/hour) - Day {i+1}", value=50.0, step=1, min_value=0.0, max_value=200.0))
    vibration.append(st.number_input(f"Vibration (Hz) - Day {i+1}", value=40.0, step=1, min_value=0.0, max_value=200.0))
    oil_condition.append(st.number_input(f"Oil Condition Index - Day {i+1}", value=50.0, step=1, min_value=0.0, max_value=100.0))
    chemical_concentration.append(st.number_input(f"Chemical Concentration (%) - Day {i+1}", value=60.0, step=1, min_value=0.0, max_value=100.0))
    energy_consumption.append(st.number_input(f"Energy Consumption (GJ) - Day {i+1}", value=35.0, step=1, min_value=0.0, max_value=100.0))
    emissions.append(st.number_input(f"Emissions (ppm) - Day {i+1}", value=50.0, step=1, min_value=0.0, max_value=200.0))
    production_unit.append(st.number_input(f"Production Unit (ton/day) - Day {i+1}", value=250.0, step=1, min_value=0.0, max_value=1000.0))

# ----------------------------
# System Health Status
# ----------------------------
st.markdown("<h3>💡 System Health Status</h3>", unsafe_allow_html=True)

def get_health_status(value, lower, upper):
    if value < lower:
        return "🔴 Low"
    elif value > upper:
        return "🔥 High"
    else:
        return "✅ Normal"

# Display illustrations for each day
for i in range(days):
    st.markdown(f"""
    <p>
    Day {i+1}: 
    Pressure: {get_health_status(pressure[i], *param_ranges['Pressure'])}, 
    Temperature: {get_health_status(temperature[i], *param_ranges['Temperature'])}, 
    Flow: {get_health_status(flow[i], *param_ranges['Flow'])}, 
    Vibration: {get_health_status(vibration[i], *param_ranges['Vibration'])}, 
    Oil Condition: {get_health_status(oil_condition[i], *param_ranges['Oil Condition'])}, 
    Chemical: {get_health_status(chemical_concentration[i], *param_ranges['Chemical Concentration'])}, 
    Energy: {get_health_status(energy_consumption[i], *param_ranges['Energy Consumption'])}, 
    Emissions: {get_health_status(emissions[i], *param_ranges['Emissions'])}, 
    Production: {get_health_status(production_unit[i], *param_ranges['Production Unit'])}
    </p>
    """, unsafe_allow_html=True)

# ----------------------------
# Risk Classification
# ----------------------------
def classify_risk(value, lower, upper):
    if value < lower:
        return "Low"
    elif value > upper:
        return "High"
    else:
        return "Normal"

if st.button("Analyze Data"):
    df = pd.DataFrame({
        "Day": [f"Day {i+1}" for i in range(days)],
        "Pressure (bar)": pressure,
        "Temperature (°C)": temperature,
        "Flow (Kg/hour)": flow,
        "Vibration (Hz)": vibration,
        "Oil Condition": oil_condition,
        "Chemical Concentration (%)": chemical_concentration,
        "Energy Consumption (GJ)": energy_consumption,
        "Emissions (ppm)": emissions,
        "Production Unit (ton/day)": production_unit
    })

    # Apply risk classification
    for col, (lower, upper) in param_ranges.items():
        df[col] = [classify_risk(df[col][i], lower, upper) for i in range(days)]

    # Display dataframe
    st.subheader("📊 Process Data and Risk Levels")
    st.dataframe(df, height=350)

    # Summary of critical events
    summary_text = ""
    for col in param_ranges.keys():
        high_days = [df['Day'][i] for i in range(days) if df[col][i]=="High"]
        low_days = [df['Day'][i] for i in range(days) if df[col][i]=="Low"]
        if high_days:
            summary_text += f"🔥 {col} High: {', '.join(high_days)}\n"
        if low_days:
            summary_text += f"🔴 {col} Low: {', '.join(low_days)}\n"
    if not summary_text:
        summary_text = "✅ All readings normal"

    st.markdown(f"""
    <div class='summary-card'>
        <h4>Summary of Critical Events</h4>
        <pre>{summary_text}</pre>
    </div>
    """, unsafe_allow_html=True)

    # Plot all numeric parameters trends
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(range(1,days+1), pressure, marker='o', label='Pressure (bar)')
    ax.plot(range(1,days+1), temperature, marker='s', label='Temperature (°C)')
    ax.plot(range(1,days+1), flow, marker='^', label='Flow (Kg/hour)')
    ax.plot(range(1,days+1), vibration, marker='v', label='Vibration (Hz)')
    ax.plot(range(1,days+1), oil_condition, marker='d', label='Oil Condition')
    ax.plot(range(1,days+1), chemical_concentration, marker='h', label='Chemical Concentration (%)')
    ax.plot(range(1,days+1), energy_consumption, marker='x', label='Energy Consumption (GJ)')
    ax.plot(range(1,days+1), emissions, marker='*', label='Emissions (ppm)')
    ax.plot(range(1,days+1), production_unit, marker='p', label='Production Unit (ton/day)')

    ax.set_xticks(range(1,days+1))
    ax.set_xticklabels([f"Day {i}" for i in range(1,days+1)])
    ax.set_title("Process Parameter Trends", fontsize=16, color='#ffb366')
    ax.set_xlabel("Day")
    ax.set_ylabel("Risk Status")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    st.pyplot(fig)
