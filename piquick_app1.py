import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="PIQuick Dashboard", layout="wide")
st.title("📊 PIQuick - Industrial Risk Dashboard")
st.write("""
Simulate PI system reports: enter daily process parameters, classify risks, and visualize trends.
""")

# ----------------------------
# Layout: Two Columns
# ----------------------------
col1, col2 = st.columns([1,2])

with col1:
    st.markdown("<h3 style='color:darkblue;'>📝 Input Daily Process Data</h3>", unsafe_allow_html=True)
    
    # Numeric Inputs
    pressure = [st.number_input(f'Day {i+1} Pressure (bar)', value=10.0, step=0.1) for i in range(5)]
    temperature = [st.number_input(f'Day {i+1} Temperature (°C)', value=65.0, step=0.1) for i in range(5)]
    flow = [st.number_input(f'Day {i+1} Flow (L/min)', value=200, step=1) for i in range(5)]
    vibration = [st.number_input(f'Day {i+1} Vibration (Hz)', value=50.0, step=0.1) for i in range(5)]
    oil_condition = [st.number_input(f'Day {i+1} Oil Condition', value=2.0, step=0.1) for i in range(5)]
    chemical_concentration = [st.number_input(f'Day {i+1} Chemical Concentration (%)', value=5.0, step=0.1) for i in range(5)]
    energy_consumption = [st.number_input(f'Day {i+1} Energy Consumption (kWh)', value=100, step=1) for i in range(5)]
    emissions = [st.number_input(f'Day {i+1} Emissions (ppm)', value=50, step=1) for i in range(5)]
    alerts = [st.selectbox(f'Day {i+1} Alert / Safety Trip', ['No', 'Yes']) for i in range(5)]
    
    # Interactive Checkboxes
    show_chart = st.checkbox("Show Trend Chart", value=True)
    highlight_high_risk = st.checkbox("Highlight High Risk Only", value=False)

# ----------------------------
# Risk Classification Function
# ----------------------------
def classify_risk(p, t, f, v, oil, chem, energy, em, alert):
    if alert == "Yes" or t>75 or p>11 or v>70 or oil>5 or chem>10 or energy>150 or em>100:
        return "High"
    elif t>65 or p>10 or v>60 or oil>3 or chem>7 or energy>120 or em>80:
        return "Medium"
    else:
        return "Low"

# ----------------------------
# Analyze Button
# ----------------------------
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
    
    # ----------------------------
    # Display Color-Coded Table
    # ----------------------------
    def color_risk(val):
        if val=="High":
            return 'background-color: red; color:white; font-weight:bold;'
        elif val=="Medium":
            return 'background-color: orange; color:white; font-weight:bold;'
        else:
            return 'background-color: green; color:white; font-weight:bold;'
    
    with col2:
        st.subheader("Process Data with Risk Levels")
        display_df = df
        if highlight_high_risk:
            display_df = df[df['Risk']=="High"]
        st.dataframe(display_df.style.applymap(color_risk, subset=['Risk']))
        
        # ----------------------------
        # Summary Card
        # ----------------------------
        high_risk_days = df[df['Risk']=="High"]['Day'].tolist()
        summary_text = "✅ All readings normal" if not high_risk_days else f"⚠️ High Risk on: {', '.join(high_risk_days)}"
        st.markdown(f"<div style='background-color:#e0f7fa;padding:15px;border-radius:10px'><h4>Summary of Critical Events</h4><pre>{summary_text}</pre></div>", unsafe_allow_html=True)
        
        # ----------------------------
        # Trend Chart
        # ----------------------------
        if show_chart:
            st.subheader("📊 Process Data Trends")
            plt.figure(figsize=(10,5))
            plt.plot(df['Day'], df['Temperature'], marker='o', label='Temperature (°C)', color='red', linewidth=2)
            plt.plot(df['Day'], df['Pressure'], marker='s', label='Pressure (bar)', color='blue', linewidth=2)
            plt.plot(df['Day'], df['Flow'], marker='^', label='Flow (L/min)', color='green', linewidth=2)
            plt.plot(df['Day'], df['Vibration'], marker='x', label='Vibration (Hz)', color='purple', linewidth=2)
            plt.plot(df['Day'], df['Oil Condition'], marker='d', label='Oil Condition', color='brown', linewidth=2)
            plt.plot(df['Day'], df['Chemical Concentration'], marker='*', label='Chemical Conc.', color='pink', linewidth=2)
            plt.plot(df['Day'], df['Energy Consumption'], marker='h', label='Energy (kWh)', color='cyan', linewidth=2)
            plt.plot(df['Day'], df['Emissions'], marker='p', label='Emissions (ppm)', color='gray', linewidth=2)
            plt.title("Process Data Overview", fontsize=16, color='darkblue')
            plt.xlabel("Day")
            plt.ylabel("Values")
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            st.pyplot(plt)
