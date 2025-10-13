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

for i in range(days):
    st.markdown(f"<h4>Day {i+1}</h4>", unsafe_allow_html=True)
    pressure.append(st.number_input(f"Pressure (bar) - Day {i+1}", value=10.0, step=0.1, min_value=0.0, max_value=20.0))
    temperature.append(st.number_input(f"Temperature (°C) - Day {i+1}", value=65.0, step=0.1, min_value=0.0, max_value=150.0))
    flow.append(st.number_input(f"Flow (L/min) - Day {i+1}", value=200, step=1, min_value=0, max_value=1000))
    vibration.append(st.number_input(f"Vibration (Hz) - Day {i+1}", value=50.0, step=0.1, min_value=0.0, max_value=200.0))
    oil_condition.append(st.number_input(f"Oil Condition Index - Day {i+1}", value=2.0, step=0.1, min_value=0.0, max_value=10.0))
    chemical_concentration.append(st.number_input(f"Chemical Concentration (%) - Day {i+1}", value=5.0, step=0.1, min_value=0.0, max_value=100.0))
    energy_consumption.append(st.number_input(f"Energy Consumption (kWh) - Day {i+1}", value=100, step=1, min_value=0, max_value=1000))
    emissions.append(st.number_input(f"Emissions (ppm) - Day {i+1}", value=50, step=1, min_value=0, max_value=1000))

# ----------------------------
# Dynamic Illustration
# ----------------------------
st.markdown("<h3>💡 System Health Status</h3>", unsafe_allow_html=True)

def get_illustration(temp, pressure):
    if temp > 75 or pressure > 11:
        return "🔥 High Risk!"
    elif temp > 65 or pressure > 10:
        return "⚠️ Moderate Risk"
    else:
        return "✅ Normal"

illustrations = [get_illustration(temperature[i], pressure[i]) for i in range(days)]

for i in range(days):
    st.markdown(f"<p>Day {i+1}: {illustrations[i]}</p>", unsafe_allow_html=True)

# ----------------------------
# Risk Classification
# ----------------------------
def classify_risk(p, t, f, v, oil, chem, energy, em):
    if t > 75 or p > 11 or v > 70 or oil > 5 or chem > 10 or energy > 150 or em > 100:
        return "High"
    elif t > 65 or p > 10 or v > 60 or oil > 3 or chem > 7 or energy > 120 or em > 80:
        return "Medium"
    else:
        return "Low"

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
    })

    df['Risk'] = [classify_risk(
        pressure[i], temperature[i], flow[i], vibration[i],
        oil_condition[i], chemical_concentration[i],
        energy_consumption[i], emissions[i]
    ) for i in range(days)]

    # Display dataframe with colors
    def color_risk(val):
        if val == "High":
            return 'background-color: red; color:white; font-weight:bold;'
        elif val == "Medium":
            return 'background-color: orange; color:white; font-weight:bold;'
        else:
            return 'background-color: green; color:white; font-weight:bold;'

    st.subheader("📊 Process Data and Risk Levels")
    st.dataframe(df.style.applymap(color_risk, subset=['Risk']), height=350)

    # Summary
    high_risk_days = df[df['Risk'] == "High"]['Day'].tolist()
    summary_text = "✅ All readings normal" if not high_risk_days else f"⚠️ High Risk on: {', '.join(high_risk_days)}"
    st.markdown(f"""
    <div class='summary-card'>
        <h4>Summary of Critical Events</h4>
        <pre>{summary_text}</pre>
    </div>
    """, unsafe_allow_html=True)

    # Trend chart - all numeric parameters
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['Day'], df['Temperature'], marker='o', label='Temperature (°C)', linewidth=2)
    ax.plot(df['Day'], df['Pressure'], marker='s', label='Pressure (bar)', linewidth=2)
    ax.plot(df['Day'], df['Flow'], marker='^', label='Flow (L/min)', linewidth=2)
    ax.plot(df['Day'], df['Vibration'], marker='v', label='Vibration (Hz)', linewidth=2)
    ax.plot(df['Day'], df['Oil Condition'], marker='d', label='Oil Condition', linewidth=2)
    ax.plot(df['Day'], df['Chemical Concentration'], marker='h', label='Chemical Concentration (%)', linewidth=2)
    ax.plot(df['Day'], df['Energy Consumption'], marker='x', label='Energy Consumption (kWh)', linewidth=2)
    ax.plot(df['Day'], df['Emissions'], marker='*', label='Emissions (ppm)', linewidth=2)
    ax.set_title("Process Parameter Trends", fontsize=16, color='#ffb366')
    ax.set_xlabel("Day")
    ax.set_ylabel("Value")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    st.pyplot(fig)
