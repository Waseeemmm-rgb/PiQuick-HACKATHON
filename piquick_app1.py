import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="SIMRAS - Smart Industrial Monitoring", layout="wide")

st.markdown("<h1 style='color:#ff8000;'>SIMRAS: Smart Industrial Monitoring & Risk Analysis System</h1>", unsafe_allow_html=True)
st.write("Automated industrial data simulation, risk detection, and AI-based prediction.")

# ----------------------------
# Parameters and limits
# ----------------------------
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

# ----------------------------
# Simulate automated data (database)
# ----------------------------
if 'params_data' not in st.session_state:
    st.session_state.params_data = {}
    for day in days:
        st.session_state.params_data[day] = {}
        for param, label in params.items():
            low, high = limits[param]
            st.session_state.params_data[day][param] = round(np.random.uniform(low, high),2)

df = pd.DataFrame([{ "Day": d, **st.session_state.params_data[d]} for d in days])

st.subheader("📊 Automatically Generated Plant Data")
st.dataframe(df)

# ----------------------------
# Risk Analysis
# ----------------------------
st.subheader("⚠️ Risk Analysis")
summary_list = []
for day in days:
    for param, label in params.items():
        val = st.session_state.params_data[day][param]
        low, high = limits[param]
        if val < low:
            summary_list.append(f"⚠️ {label} (Value: {val}) is BELOW {low} on {day}")
        elif val > high:
            summary_list.append(f"🔥 {label} (Value: {val}) is ABOVE {high} on {day}")

if summary_list:
    st.markdown("\n".join(summary_list))
else:
    st.success("✅ All parameters within normal range!")

# ----------------------------
# Trend Graphs
# ----------------------------
st.subheader("📈 Parameter Trends Over Days")
plot_df = df.set_index("Day")
fig, ax = plt.subplots(figsize=(12,5))
for param, label in params.items():
    ax.plot(plot_df.index, plot_df[param], marker="o", label=label)
ax.set_xlabel("Day")
ax.set_ylabel("Value")
ax.set_title("Industrial Parameter Trends")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend(loc='center left', bbox_to_anchor=(1,0.5))
st.pyplot(fig)

# ----------------------------
# AI Prediction for Next Day
# ----------------------------
st.subheader("🔮 AI Prediction for Next Day")
if st.button("Predict Day 6 Values"):
    next_day = {}
    for param in params:
        X = np.array(range(1,len(days)+1)).reshape(-1,1)
        y = np.array([st.session_state.params_data[d][param] for d in days])
        model = LinearRegression().fit(X, y)
        next_day[param] = float(model.predict([[len(days)+1]])[0])

    st.write("Predicted values for Day 6:")
    st.dataframe(pd.DataFrame([next_day], index=["Day 6"]))

    # Highlight predicted risks
    pred_risks = []
    for param, val in next_day.items():
        low, high = limits[param]
        if val < low:
            pred_risks.append(f"⚠️ {params[param]} predicted BELOW {low} ({val:.2f})")
        elif val > high:
            pred_risks.append(f"🔥 {params[param]} predicted ABOVE {high} ({val:.2f})")

    if pred_risks:
        st.warning("\n".join(pred_risks))
    else:
        st.success("✅ Predicted values within normal range")
