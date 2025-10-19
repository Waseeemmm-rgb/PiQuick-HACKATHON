# simras_app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import time
from datetime import datetime, timedelta

# ----------------------------
# Page config and helper
# ----------------------------
st.set_page_config(page_title="SIMRAS 2.0 - AI Plant Advisor & Optimizer", layout="wide")
st.title("SIMRAS 2.0 — AI Plant Advisor & Sustainability Optimizer")
st.caption("Prototype for academic research — simulated data. Author: Mohammed Waseem Attar, Dhofar University")

# ----------------------------
# PARAMETERS, LIMITS, INITIAL SIMULATION SETTINGS
# ----------------------------
DAYS = 30  # simulated historical days
np.random.seed(42)

PARAMS = {
    "pressure": ("Pressure (bar)", 20.0, 50.0),
    "temperature": ("Temperature (°C)", 200.0, 300.0),
    "flow": ("Flow (Kg/hour)", 1.0, 100.0),
    "vibration": ("Vibration (Hz)", 10.0, 80.0),
    "oil_condition": ("Oil Condition Index", 20.0, 80.0),
    "chemical_concentration": ("Chemical Concentration (%)", 30.0, 90.0),
    "energy_consumption": ("Energy Consumption (GJ)", 25.0, 50.0),
    "emissions": ("Emissions (%)", 1.0, 30.0),
    "production_unit": ("Production Unit (ton/day)", 50.0, 500.0)
}

# ----------------------------
# Simulated automated DB (stream of daily aggregates)
# Each day has natural small random walk + occasional drift/outlier events
# ----------------------------
@st.cache_data
def generate_simulated_db(days=DAYS):
    base = {}
    for p, (label, low, high) in PARAMS.items():
        # start at mid-range
        start = (low + high) / 2.0
        # produce a random walk with small daily variations
        vals = [start]
        for i in range(1, days):
            drift = np.random.normal(loc=0.0, scale=(high - low) * 0.01)  # small noise
            # occasional larger event
            if np.random.rand() < 0.03:
                drift += np.random.normal(loc=0.0, scale=(high - low) * 0.1)
            new = max(low * 0.5, min(high * 1.5, vals[-1] + drift))  # keep bounded
            vals.append(round(new, 2))
        base[p] = vals
    dates = [ (datetime.now() - timedelta(days=(days - 1 - i))).date().isoformat() for i in range(days) ]
    df = pd.DataFrame({ "date": dates })
    for p in PARAMS:
        df[p] = base[p]
    # Add an "operator" column simulating shift or manual overrides occasionally
    df["operator_override"] = [ True if np.random.rand() < 0.05 else False for _ in range(days) ]
    return df

df_db = generate_simulated_db()

# ----------------------------
# Sidebar: select plant / data source & quick controls
# ----------------------------
st.sidebar.header("SIMRAS Controls")
plant_id = st.sidebar.selectbox("Plant / Unit", ["OQBI_Salalah_Unit1", "Demo_Plant_A"])
simulate_new = st.sidebar.button("Simulate new database")
if simulate_new:
    df_db = generate_simulated_db()
    st.experimental_rerun()

days_to_show = st.sidebar.slider("Days to show", min_value=7, max_value=DAYS, value=30, step=1)
df = df_db.tail(days_to_show).reset_index(drop=True)

# ----------------------------
# Utility functions
# ----------------------------
def check_limits(value, param):
    _, low, high = PARAMS[param]
    if value < low:
        return "LOW"
    elif value > high:
        return "HIGH"
    else:
        return "OK"

def simple_predict(series):
    """
    Simple linear prediction for next point using numpy.polyfit degree 1.
    Returns predicted value and slope.
    """
    y = np.array(series, dtype=float)
    x = np.arange(1, len(y)+1)
    if len(y) < 2:
        return float(y[-1]), 0.0
    coeffs = np.polyfit(x, y, 1)  # slope, intercept
    slope, intercept = coeffs[0], coeffs[1]
    next_x = len(y) + 1
    pred = float(np.polyval(coeffs, next_x))
    return round(pred, 3), float(slope)

def energy_intensity(energy_gj, production_ton):
    # simple energy intensity metric: GJ per ton
    if production_ton <= 0:
        return None
    return energy_gj / production_ton

# ----------------------------
# Tabs / Modules for 5 projects
# ----------------------------
tabs = st.tabs(["Overview", "AI Plant Advisor", "Digital Twin / Optimizer", "Maintenance Predictor", "Human Risk Monitor", "Sustainability"])

# ----------------------------
# Overview Tab
# ----------------------------
with tabs[0]:
    st.header("Overview & Live Snapshot")
    st.markdown("""
    **SIMRAS 2.0** integrates:
    - AI-driven **Plant Advisor** (actionable recommendations),
    - **Digital Twin / Optimizer** for energy & emissions savings,
    - **Maintenance Predictor** with cost/downtime estimation,
    - **Human Error & Shift Monitor**,
    - **Sustainability Dashboard** (energy intensity & emissions).
    """)
    st.subheader("Latest data (last {} days)".format(days_to_show))
    st.dataframe(df.set_index("date"))
    st.markdown("**Quick automatic risk scan** (based on parameter ranges):")
    risk_rows = []
    for idx, row in df.iterrows():
        for p in PARAMS:
            if p == "production_unit": continue
            status = check_limits(row[p], p)
            if status != "OK":
                risk_rows.append(f"{row['date']}: {PARAMS[p][0]} = {row[p]} ({status})")
    if risk_rows:
        st.warning("\n".join(risk_rows))
    else:
        st.success("No out-of-range values in the shown period.")

# ----------------------------
# AI Plant Advisor Tab (Project 1)
# ----------------------------
with tabs[1]:
    st.header("AI-Powered Plant Advisor")
    st.markdown("This module predicts near-term risks and provides simple, actionable recommendations.")
    st.markdown("**How it works (prototype)**: uses short-window trend prediction (linear) and rule-based mapping to recommended actions.")
    st.subheader("Predictions & Warnings for Next Day (Day+1)")
    preds = {}
    slopes = {}
    for p in PARAMS:
        val_series = df[p].values
        pred, slope = simple_predict(val_series)
        preds[p] = pred
        slopes[p] = slope
    pred_df = pd.DataFrame([preds], index=["predicted_day_plus_1"])
    st.dataframe(pred_df.T.rename(columns={0:"predicted"}))
    # generate recommendations:
    recs = []
    for p in PARAMS:
        label = PARAMS[p][0]
        pred = preds[p]
        status = check_limits(pred, p)
        # simple rules for recommendations
        if status == "HIGH":
            if p in ["pressure", "temperature", "vibration"]:
                recs.append((label, pred, "Reduce process load by 5-10% and inspect related equipment. Consider controlled cool-down."))
            elif p in ["emissions", "energy_consumption"]:
                recs.append((label, pred, "Investigate inefficient stages; reduce throughput temporarily and check catalysts/heat exchangers."))
            else:
                recs.append((label, pred, "Investigate parameter source and check control valves/sensors."))
        elif status == "LOW":
            recs.append((label, pred, "Review setpoints; consider increasing feed/input or check sensor calibration."))
        else:
            # if slope steep positive & near upper bound
            _, low, high = PARAMS[p]
            if slopes[p] > 0 and pred > (low + 0.75*(high - low)):
                recs.append((label, pred, "Trend rising quickly — schedule monitoring and possible early intervention."))
    if recs:
        st.subheader("Recommendations (actionable)")
        for label, val, text in recs:
            st.markdown(f"- **{label}** predicted = **{val:.2f}** → *{text}*")
    else:
        st.info("No immediate recommendations — predicted values within safe bounds.")

    # Provide confidence & log
    st.markdown("**Advisor Confidence & Notes**: This prototype uses linear trend fitting on daily aggregates. For production, use higher-frequency data and model ensembles (LSTM, XGBoost) and integrate process constraints.")

# ----------------------------
# Digital Twin / Optimizer Tab (Project 2)
# ----------------------------
with tabs[2]:
    st.header("Digital Twin & Energy Optimizer (Proof of concept)")
    st.markdown("This is a lightweight 'what-if' model that estimates energy consumption & emissions from simple parameter changes.")
    st.subheader("Current energy intensity")
    last = df.iloc[-1]
    ei = energy_intensity(last["energy_consumption"], last["production_unit"])
    st.write(f"Latest Energy Consumption: {last['energy_consumption']} GJ, Production: {last['production_unit']} ton/day")
    st.write(f"Energy Intensity = {ei:.3f} GJ / ton")

    st.subheader("What-if optimizer (change parameters and estimate energy impact)")
    st.markdown("Simplified assumption: energy consumption is roughly proportional to a weighted sum of temperature, flow and production.")
    w_temp, w_flow, w_prod = 0.5, 0.3, 0.2  # example weights
    temp_change = st.number_input("Temperature change (Δ°C)", value=0.0, step=1.0)
    flow_change_pct = st.number_input("Flow change (%)", value=0.0, step=1.0)
    prod_change_pct = st.number_input("Production change (%)", value=0.0, step=1.0)
    if st.button("Run optimizer simulation"):
        # baseline
        base_temp = last["temperature"]
        base_flow = last["flow"]
        base_prod = last["production_unit"]
        est_energy = last["energy_consumption"]
        # naive model:
        new_temp = base_temp + temp_change
        new_flow = base_flow * (1 + flow_change_pct/100.0)
        new_prod = base_prod * (1 + prod_change_pct/100.0)
        # energy scaling:
        energy_factor = (w_temp * (new_temp/base_temp) + w_flow * (new_flow/base_flow) + w_prod * (new_prod/base_prod))
        new_energy = est_energy * energy_factor
        new_ei = energy_intensity(new_energy, new_prod)
        st.success(f"Estimated new energy consumption: {new_energy:.2f} GJ, Energy intensity: {new_ei:.3f} GJ/ton")
        diff_percent = (new_energy - est_energy) / est_energy * 100.0
        if diff_percent < 0:
            st.info(f"Estimated energy saving: {abs(diff_percent):.2f}%")
        else:
            st.warning(f"Estimated energy increase: {diff_percent:.2f}%")
        # suggest if beneficial
        if new_ei and new_ei < ei:
            st.write("✅ Optimization suggestion: parameter changes may reduce energy intensity.")
        else:
            st.write("❌ Not recommended - energy intensity rises.")

    st.markdown("**Note:** This is a conceptual digital twin. A production twin requires physics-based models and validated plant data.")

# ----------------------------
# Maintenance Predictor Tab (Project 3)
# ----------------------------
with tabs[3]:
    st.header("Maintenance Predictor & Cost Estimator")
    st.markdown("Uses trend of vibration and oil condition to estimate failure probability window (prototype).")
    st.subheader("Latest health indicators")
    st.write(f"Vibration: {last['vibration']}, Oil Condition Index: {last['oil_condition']}")
    # compute moving average and trend on vibration
    vib_series = df["vibration"].astype(float)
    oil_series = df["oil_condition"].astype(float)
    vib_pred, vib_slope = simple_predict(vib_series)
    oil_pred, oil_slope = simple_predict(oil_series)

    st.write(f"Predicted vibration next day: {vib_pred:.2f} (slope {vib_slope:.4f})")
    st.write(f"Predicted oil condition next day: {oil_pred:.2f} (slope {oil_slope:.4f})")

    # simple failure risk model:
    failure_risk = 0.0
    # if vibration trending up and crosses 80% of max => high risk
    vib_threshold = PARAMS["vibration"][2] * 0.9
    if vib_pred >= vib_threshold or vib_slope > 0.5:
        failure_risk += 0.6
    # if oil condition is poor (<30) or trending down:
    if oil_pred < 30 or oil_slope < -0.5:
        failure_risk += 0.4

    failure_risk = min(1.0, failure_risk)
    st.metric("Estimated component failure risk (0-1)", f"{failure_risk:.2f}")

    # cost estimate heuristic
    if failure_risk > 0.7:
        est_downtime_days = np.random.randint(3,10)
        est_cost = est_downtime_days * last["production_unit"] * 50  # placeholder OMR per day lost revenue
        st.error(f"High failure risk predicted — estimated downtime: {est_downtime_days} days. Approx. lost revenue: {est_cost:.0f} (units). Recommend immediate inspection.")
    elif failure_risk > 0.3:
        st.warning("Moderate risk. Plan inspection within next 72 hours.")
    else:
        st.success("Low immediate risk. Monitor per normal schedule.")

    st.markdown("**Maintenance suggestion examples** (prototype):")
    st.write("- If vibration rising: schedule bearing inspection; check misalignment, looseness.")
    st.write("- If oil condition degrading: sample & replace oil; check seals and contamination sources.")

# ----------------------------
# Human Risk Monitor Tab (Project 4)
# ----------------------------
with tabs[4]:
    st.header("Human Error & Shift Monitor")
    st.markdown("Prototype simulating operator overrides and a fatigue/error index based on time-of-day and overrides.")
    st.subheader("Operator override log (simulated)")
    ops = []
    # create a simulated list of operator actions across days
    for i, r in df.iterrows():
        if r["operator_override"]:
            ops.append({"date": r["date"], "operator": f"Op{np.random.randint(1,6)}", "action":"override_setpoint", "notes":"manual adj"})
    if ops:
        st.table(pd.DataFrame(ops))
    else:
        st.write("No overrides logged in the simulated period.")

    # simple human risk index: count overrides in last 7 days + night shift weight
    last7 = df.tail(7)
    overrides = int(last7["operator_override"].sum())
    # simulated night shift factor (random)
    night_shifts = np.random.randint(0,3)
    human_risk_index = min(1.0, (overrides * 0.15 + night_shifts * 0.1))
    st.metric("Human Risk Index (0-1)", f"{human_risk_index:.2f}")
    if human_risk_index > 0.4:
        st.warning("Elevated human-related risk. Recommend cross-checks, additional training, and enforced handover procedures.")

# ----------------------------
# Sustainability Tab (Project 5)
# ----------------------------
with tabs[5]:
    st.header("Sustainability Dashboard")
    st.markdown("Energy & emissions KPI calculations and simple suggestions to reduce carbon intensity.")
    st.subheader("Historical energy intensity (GJ/ton)")
    df_ei = []
    for _, r in df.iterrows():
        ei_val = energy_intensity(r["energy_consumption"], r["production_unit"])
        df_ei.append({"date": r["date"], "energy_intensity": round(ei_val,3) if ei_val else None, "emissions": r["emissions"]})
    df_ei = pd.DataFrame(df_ei).set_index("date")
    st.line_chart(df_ei[["energy_intensity","emissions"]])

    st.subheader("KPI Summary (latest)")
    st.write(f"- Latest energy intensity: {df_ei['energy_intensity'].iloc[-1]:.3f} GJ/ton")
    st.write(f"- Latest emissions: {df['emissions'].iloc[-1]:.2f}%")

    # Quick sustainability suggestions
    st.markdown("**Suggested actions (prototype)**:")
    st.write("- Optimize heat exchanger cleaning schedule to improve thermal efficiency.")
    st.write("- Use optimizer module (Digital Twin) to find parameter settings that reduce energy intensity.")
    st.write("- Plan renewable energy sourcing or waste heat recovery for long-term decarbonization.")

# ----------------------------
# Export / Reporting utilities
# ----------------------------
st.sidebar.header("Export")
if st.sidebar.button("Download consolidated CSV report"):
    buffer = io.StringIO()
    # combine latest, prediction, advisor summary
    # Create a compact report df
    report_df = df.copy()
    # append predicted row
    pred_row = { "date": "pred_day_plus_1" }
    for p in PARAMS:
        pred_val, _ = simple_predict(df[p].values)
        pred_row[p] = pred_val
    pred_row["operator_override"] = False
    report_df = pd.concat([report_df, pd.DataFrame([pred_row])], ignore_index=True)
    report_df.to_csv(buffer, index=False)
    st.sidebar.download_button("Download CSV", data=buffer.getvalue(), file_name=f"SIMRAS_report_{plant_id}.csv", mime="text/csv")

st.sidebar.markdown("---")
st.sidebar.write("Prototype notes: This system uses simulated data. For production, integrate with plant historian/SCADA via secure connectors (OPC UA / MQTT), use validated physics-based digital twins and industrial-grade ML models. Ensure cybersecurity and access control when connecting to real plant systems.")
