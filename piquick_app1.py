import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Page Setup & Styling
# ----------------------------
st.set_page_config(page_title="PIQuick Dashboard", layout="wide")

st.markdown("""
    <style>
        .main {
            background-color: #f8fbfd;
        }
        h1 {
            text-align: center;
            color: #003366;
        }
        .title-banner {
            background: linear-gradient(90deg, #003366, #0073b1);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .summary-box {
            background-color: #e0f7fa;
            padding: 15px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 500;
        }
        .risk-card {
            background-color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Header Section with Logo
# ----------------------------
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/97/OQ_logo.png", width=90)
with col_title:
    st.markdown("<div class='title-banner'><h1>📊 PIQuick – Industrial Risk Dashboard (OQBI Oman)</h1></div>", unsafe_allow_html=True)
st.write("Monitor and analyze daily industrial process data to detect early risk patterns and improve safety and efficiency.")

st.divider()

# ----------------------------
# Layout: Input and Output
# ----------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<h3 style='color:#003366;'>🧮 Input Daily Parameters</h3>", unsafe_allow_html=True)
    days = [f"Day {i+1}" for i in range(5)]

    pressure = [st.slider(f'{d} Pressure (bar)', 5.0, 15.0, 10.0, 0.1) for d in days]
    temperature = [st.slider(f'{d} Temperature (°C)', 40.0, 100.0, 65.0, 0.5) for d in days]
    flow = [st.slider(f'{d} Flow (L/min)', 100, 400, 200, 5) for d in days]
    vibration = [st.slider(f'{d} Vibration (Hz)', 20.0, 100.0, 50.0, 0.5) for d in days]
    oil_condition = [st.slider(f'{d} Oil Condition Index', 0.5, 10.0, 2.0, 0.1) for d in days]
    chemical_concentration = [st.slider(f'{d} Chemical Conc. (%)', 1.0, 15.0, 5.0, 0.1) for d in days]
    energy_consumption = [st.slider(f'{d} Energy (kWh)', 50, 200, 100, 5) for d in days]
    emissions = [st.slider(f'{d} Emissions (ppm)', 20, 200, 50, 5) for d in days]
    alerts = [st.selectbox(f'{d} Alert / Trip', ['No', 'Yes']) for d in days]

    show_chart = st.toggle("📈 Show Trend Chart", value=True)
    highlight_high_risk = st.toggle("🚨 Highlight High Risk Only", value=False)

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
with col2:
    if st.button("🔍 Analyze Data", use_container_width=True):
        df = pd.DataFrame({
            "Day": days,
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

        df['Risk'] = [
            classify_risk(pressure[i], temperature[i], flow[i], vibration[i],
                          oil_condition[i], chemical_concentration[i],
                          energy_consumption[i], emissions[i], alerts[i])
            for i in range(5)
        ]

        # ----------------------------
        # Color Coding Function
        # ----------------------------
        def color_risk(val):
            if val == "High":
                return 'background-color: red; color:white; font-weight:bold;'
            elif val == "Medium":
                return 'background-color: orange; color:white; font-weight:bold;'
            else:
                return 'background-color: green; color:white; font-weight:bold;'

        st.markdown("<h3 style='color:#003366;'>📋 Process Data Overview</h3>", unsafe_allow_html=True)

        display_df = df if not highlight_high_risk else df[df['Risk'] == "High"]
        st.dataframe(display_df.style.applymap(color_risk, subset=['Risk']), height=320)

        # ----------------------------
        # Summary
        # ----------------------------
        high_risk_days = df[df['Risk']=="High"]['Day'].tolist()
        summary_text = "✅ All readings normal and safe." if not high_risk_days else f"⚠️ High risk detected on: {', '.join(high_risk_days)}"

        st.markdown(f"<div class='summary-box'><h4>Summary of Critical Events</h4>{summary_text}</div>", unsafe_allow_html=True)

        # ----------------------------
        # Trend Chart
        # ----------------------------
        if show_chart:
            st.markdown("<h3 style='color:#003366;'>📊 Process Data Trends</h3>", unsafe_allow_html=True)
            plt.figure(figsize=(10,5))
            plt.plot(df['Day'], df['Temperature'], marker='o', label='Temperature (°C)', color='red', linewidth=2)
            plt.plot(df['Day'], df['Pressure'], marker='s', label='Pressure (bar)', color='blue', linewidth=2)
            plt.plot(df['Day'], df['Flow'], marker='^', label='Flow (L/min)', color='green', linewidth=2)
            plt.plot(df['Day'], df['Vibration'], marker='x', label='Vibration (Hz)', color='purple', linewidth=2)
            plt.plot(df['Day'], df['Energy Consumption'], marker='h', label='Energy (kWh)', color='cyan', linewidth=2)
            plt.plot(df['Day'], df['Emissions'], marker='p', label='Emissions (ppm)', color='gray', linewidth=2)
            plt.title("Process Data Overview", fontsize=16, color='darkblue')
            plt.xlabel("Day")
            plt.ylabel("Value")
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            st.pyplot(plt)
