import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# PAGE + STYLE
# ----------------------------
st.set_page_config(page_title="PIQuick - OQBI", layout="wide")
st.markdown(
    """
    <style>
        .banner {
            background: linear-gradient(90deg,#003366,#0073b1);
            padding: 14px;
            border-radius: 8px;
            color: white;
            text-align: center;
        }
        .section-box { background-color: #f2f9ff; padding:10px; border-radius:8px; }
        .summary-box { background-color: #e8f6f9; padding:12px; border-radius:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# HEADER WITH LOGO
# ----------------------------
logo_url = "https://upload.wikimedia.org/wikipedia/commons/9/97/OQ_logo.png"
st.markdown("<div style='text-align:center; margin-bottom:8px;'>", unsafe_allow_html=True)
st.image(logo_url, width=120)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='banner'><h2 style='margin:0'>PIQuick — Industrial Risk Dashboard (OQBI Oman)</h2></div>", unsafe_allow_html=True)
st.markdown("Enter daily readings. Use sliders for quick input and number boxes for precise override. Both stay synchronized for clarity.")

st.divider()

# ----------------------------
# TABS
# ----------------------------
tab_input, tab_results, tab_charts = st.tabs(["📝 Input", "📋 Results", "📊 Charts & Export"])
days = 5  # number of days shown

# ----------------------------
# SYNC FUNCTION FOR SLIDER + NUMBER INPUT
# ----------------------------
def param_inputs(label, slider_min, slider_max, slider_step, default_value, num_step, key):
    # session state sync
    if f"{key}_value" not in st.session_state:
        st.session_state[f"{key}_value"] = default_value

    col1, col2 = st.columns([1, 1])

    slider_val = col1.slider(
        f"{label} (quick adjust)",
        min_value=slider_min,
        max_value=slider_max,
        step=slider_step,
        value=st.session_state[f"{key}_value"],
        key=f"{key}_slider",
    )

    num_val = col2.number_input(
        f"{label} (precise input)",
        min_value=slider_min,
        max_value=slider_max,
        step=num_step,
        value=st.session_state[f"{key}_value"],
        key=f"{key}_num",
        format="%.2f",
    )

    # keep synced
    if slider_val != st.session_state[f"{key}_value"]:
        st.session_state[f"{key}_value"] = slider_val
    elif num_val != st.session_state[f"{key}_value"]:
        st.session_state[f"{key}_value"] = num_val

    return st.session_state[f"{key}_value"]

# ----------------------------
# INPUT TAB
# ----------------------------
with tab_input:
    st.header("Input Data Sections")

    # --- Core Process ---
    st.subheader("Core Process Parameters")
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    core_values = {"Pressure": [], "Temperature": [], "Flow": []}
    for i in range(days):
        st.markdown(f"**Day {i+1}**")
        p = param_inputs("Pressure (bar)", 0.0, 25.0, 0.1, 10.0, 0.1, f"day{i+1}_pressure")
        t = param_inputs("Temperature (°C)", 0.0, 150.0, 0.5, 65.0, 0.1, f"day{i+1}_temp")
        f = param_inputs("Flow (L/min)", 0.0, 1000.0, 1.0, 200.0, 1.0, f"day{i+1}_flow")
        core_values["Pressure"].append(p)
        core_values["Temperature"].append(t)
        core_values["Flow"].append(f)
        st.markdown("---")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Mechanical ---
    st.subheader("Mechanical Parameters")
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    vib_values = []
    for i in range(days):
        v = param_inputs("Vibration (Hz)", 0.0, 200.0, 0.5, 50.0, 0.1, f"day{i+1}_vibration")
        vib_values.append(v)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Oil & Chemical ---
    st.subheader("Oil & Chemical Parameters")
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    oil_values, chem_values = [], []
    for i in range(days):
        oil = param_inputs("Oil Condition (index)", 0.0, 10.0, 0.1, 2.0, 0.1, f"day{i+1}_oil")
        chem = param_inputs("Chemical Conc. (%)", 0.0, 100.0, 0.1, 5.0, 0.1, f"day{i+1}_chem")
        oil_values.append(oil)
        chem_values.append(chem)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Energy & Environment ---
    st.subheader("Energy & Environment")
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    energy_values, emis_values = [], []
    for i in range(days):
        energy = param_inputs("Energy Consumption (kWh)", 0.0, 1000.0, 1.0, 100.0, 1.0, f"day{i+1}_energy")
        emis = param_inputs("Emissions (ppm)", 0.0, 1000.0, 1.0, 50.0, 1.0, f"day{i+1}_emissions")
        energy_values.append(energy)
        emis_values.append(emis)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Alerts ---
    st.subheader("Alerts / Safety Trips")
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    alerts = [st.selectbox(f"Day {i+1} Alert / Trip", ["No", "Yes"], key=f"alert_{i}") for i in range(days)]
    st.markdown("</div>", unsafe_allow_html=True)

    st.success("✅ Inputs synchronized and saved. Switch to Results or Charts tab to analyze.")

# ----------------------------
# RISK LOGIC
# ----------------------------
def classify_risk(p, t, f, v, oil, chem, energy, em, alert):
    if alert == "Yes" or t > 75 or p > 11 or v > 70 or oil > 5 or chem > 10 or energy > 150 or em > 100:
        return "High"
    elif t > 65 or p > 10 or v > 60 or oil > 3 or chem > 7 or energy > 120 or em > 80:
        return "Medium"
    else:
        return "Low"

# ----------------------------
# RESULTS TAB
# ----------------------------
with tab_results:
    st.header("Results — Risk Table & Summary")

    df = pd.DataFrame({
        "Day": [f"Day {i+1}" for i in range(days)],
        "Pressure": core_values["Pressure"],
        "Temperature": core_values["Temperature"],
        "Flow": core_values["Flow"],
        "Vibration": vib_values,
        "Oil Condition": oil_values,
        "Chemical Concentration": chem_values,
        "Energy Consumption": energy_values,
        "Emissions": emis_values,
        "Alert": alerts
    })

    df["Risk"] = [
        classify_risk(df.loc[i, "Pressure"], df.loc[i, "Temperature"], df.loc[i, "Flow"],
                      df.loc[i, "Vibration"], df.loc[i, "Oil Condition"],
                      df.loc[i, "Chemical Concentration"], df.loc[i, "Energy Consumption"],
                      df.loc[i, "Emissions"], df.loc[i, "Alert"])
        for i in range(len(df))
    ]

    def color_risk(val):
        if val == "High": return "background-color:red;color:white;font-weight:bold;"
        if val == "Medium": return "background-color:orange;color:white;font-weight:bold;"
        return "background-color:green;color:white;font-weight:bold;"

    st.dataframe(df.style.applymap(color_risk, subset=["Risk"]), height=380)

    high = df[df["Risk"] == "High"]["Day"].tolist()
    if high:
        st.markdown(f"<div class='summary-box'><b>⚠️ High risk detected on:</b> {', '.join(high)}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='summary-box'>✅ No high-risk days detected.</div>", unsafe_allow_html=True)

# ----------------------------
# CHARTS TAB
# ----------------------------
with tab_charts:
    st.header("Charts & Export")

    show_temp = st.checkbox("Temperature", value=True)
    show_pressure = st.checkbox("Pressure", value=True)
    show_flow = st.checkbox("Flow", value=True)
    show_vibration = st.checkbox("Vibration", value=False)
    show_oil = st.checkbox("Oil Condition", value=False)
    show_chem = st.checkbox("Chemical Conc.", value=False)
    show_energy = st.checkbox("Energy", value=False)
    show_emis = st.checkbox("Emissions", value=False)

    fig, ax = plt.subplots(figsize=(11, 5))
    x = df["Day"]
    if show_temp: ax.plot(x, df["Temperature"], marker="o", label="Temperature (°C)", color="red", linewidth=2)
    if show_pressure: ax.plot(x, df["Pressure"], marker="s", label="Pressure (bar)", color="blue", linewidth=2)
    if show_flow: ax.plot(x, df["Flow"], marker="^", label="Flow (L/min)", color="green", linewidth=2)
    if show_vibration: ax.plot(x, df["Vibration"], marker="x", label="Vibration (Hz)", color="purple", linewidth=2)
    if show_oil: ax.plot(x, df["Oil Condition"], marker="d", label="Oil Condition", color="brown", linewidth=2)
    if show_chem: ax.plot(x, df["Chemical Concentration"], marker="*", label="Chemical Conc.", color="magenta", linewidth=2)
    if show_energy: ax.plot(x, df["Energy Consumption"], marker="h", label="Energy (kWh)", color="cyan", linewidth=2)
    if show_emis: ax.plot(x, df["Emissions"], marker="p", label="Emissions (ppm)", color="gray", linewidth=2)

    ax.set_xlabel("Day")
    ax.set_ylabel("Value")
    ax.set_title("Process Parameter Trends")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    st.pyplot(fig)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="piquick_report.csv", mime="text/csv")
