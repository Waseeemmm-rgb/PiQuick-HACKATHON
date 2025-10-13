import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="PIQuick Dashboard", layout="wide")

# ----------------------------
# Logo at the top
# ----------------------------
logo_base64 = "data:image/jpeg;base64,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"

st.markdown(
    f"""
    <div style="text-align:center; margin-bottom:20px;">
        <img src="{logo_base64}" width="150" style="border-radius:15px;">
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Header
# ----------------------------
st.markdown("""
<div style="background-color:#003366;padding:15px;border-radius:10px;text-align:center;">
    <h1 style="color:white;">OQBI Oman - PIQuick Risk Dashboard</h1>
</div>
""", unsafe_allow_html=True)

st.write("Monitor industrial parameters, detect anomalies, and visualize trends easily.")

# ----------------------------
# Layout for Inputs
# ----------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<h3 style='color:darkblue;'>📝 Input Daily Process Data</h3>", unsafe_allow_html=True)
    
    # Input fields for 5 days
    pressure = [st.number_input(f'Day {i+1} Pressure (bar)', value=10.0, step=0.1) for i in range(5)]
    temperature = [st.number_input(f'Day {i+1} Temperature (°C)', value=65.0, step=0.1) for i in range(5)]
    flow = [st.number_input(f'Day {i+1} Flow (L/min)', value=200, step=1) for i in range(5)]
    vibration = [st.number_input(f'Day {i+1} Vibration (Hz)', value=50.0, step=0.1) for i in range(5)]
    oil_condition = [st.number_input(f'Day {i+1} Oil Condition', value=2.0, step=0.1) for i in range(5)]
    chemical_concentration = [st.number_input(f'Day {i+1} Chemical Concentration (%)', value=5.0, step=0.1) for i in range(5)]
    energy_consumption = [st.number_input(f'Day {i+1} Energy Consumption (kWh)', value=100, step=1) for i in range(5)]
    emissions = [st.number_input(f'Day {i+1} Emissions (ppm)', value=50, step=1) for i in range(5)]
    alerts = [st.selectbox(f'Day {i+1} Alert / Safety Trip', ['No', 'Yes']) for i in range(5)]

# ----------------------------
# Dynamic Illustration
# ----------------------------
def get_illustration(temp, pressure):
    if temp > 75 or pressure > 11:
        return "🔥 High Risk!"
    elif temp > 65 or pressure > 10:
        return "⚠️ Moderate Risk"
    else:
        return "✅ Normal"

illustrations = [get_illustration(temperature[i], pressure[i]) for i in range(5)]
st.markdown("### System Health Status (based on inputs)")
for i in range(5):
    st.write(f"Day {i+1}: {illustrations[i]}")

# ----------------------------
# Risk Classification
# ----------------------------
def classify_risk(p, t, f, v, oil, chem, energy, em, alert):
    if alert == "Yes" or t > 75 or p > 11 or v > 70 or oil > 5 or chem > 10 or energy > 150 or em > 100:
        return "High"
    elif t > 65 or p > 10 or v > 60 or oil > 3 or chem > 7 or energy > 120 or em > 80:
        return "Medium"
    else:
        return "Low"

if st.button("Analyze Data"):
    df = pd.DataFrame({
        "Day": [f"Day {i+1}" for i in range(5)],
        "Pressure": pressure,
        "Temperature": temperature,
        "Flow": flow,
        "Vibration": vibration,
        "Oil Condition": oil_condition,
        "Chemical Concentration": chemical_concentration,
        "Energy Consumption": energy_consumption,
        "Emissions": emissions,
        "Alert": alerts
    })
    
    df['Risk'] = [classify_risk(pressure[i], temperature[i], flow[i], vibration[i], oil_condition[i],
                                chemical_concentration[i], energy_consumption[i], emissions[i], alerts[i])
                  for i in range(5)]
    
    with col2:
        st.subheader("Process Data and Risk Levels")
        
        def color_risk(val):
            if val == "High":
                return 'background-color: red; color:white; font-weight:bold;'
            elif val == "Medium":
                return 'background-color: orange; color:white; font-weight:bold;'
            else:
                return 'background-color: green; color:white; font-weight:bold;'
        
        st.dataframe(df.style.applymap(color_risk, subset=['Risk']))
        
        high_risk_days = df[df['Risk'] == "High"]['Day'].tolist()
        summary_text = "✅ All readings normal" if not high_risk_days else f"⚠️ High Risk on: {', '.join(high_risk_days)}"
        
        st.markdown(f"""
        <div style='background-color:#f0f8ff;padding:15px;border-radius:10px'>
            <h4>Summary of Critical Events</h4>
            <pre>{summary_text}</pre>
        </div>
        """, unsafe_allow_html=True)
        
        # Trend chart
        plt.figure(figsize=(10, 5))
        plt.plot(df['Day'], df['Temperature'], marker='o', label='Temperature (°C)', color='red')
        plt.plot(df['Day'], df['Pressure'], marker='s', label='Pressure (bar)', color='blue')
        plt.title("Process Data Trends", fontsize=16, color='darkblue')
        plt.xlabel("Day")
        plt.ylabel("Value")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        st.pyplot(plt)
