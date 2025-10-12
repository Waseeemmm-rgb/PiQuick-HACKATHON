import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="PIQuick Dashboard", layout="wide")

# Add Header with Logo and Title
st.markdown("""
<div style="background-color:#003366;padding:15px;border-radius:10px;text-align:center;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/0/0b/OQ_Company_Logo.png" 
         alt="OQBI Oman" width="100">
    <h1 style="color:white;">OQBI Oman - PIQuick Risk Dashboard</h1>
</div>
""", unsafe_allow_html=True)

st.write("Monitor industrial parameters, detect anomalies, and visualize trends easily.")

# ----------------------------
# Layout
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
