import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------------------
# Page Config & Styles
# ----------------------------
st.set_page_config(page_title="PIQuick - OQBI", layout="wide")

st.markdown("""
<style>
    body {background-color: #f0f4f8;}
    .banner {
        background: linear-gradient(90deg,#003366,#0073b1);
        padding: 18px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .section-box {
        background-color: #e6f0ff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .summary-box {
        background-color: #cce6ff;
        padding: 12px;
        border-radius: 10px;
        font-weight: bold;
    }
    .emoji {
        font-size: 24px;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Header with logo
# ----------------------------
logo_url = "https://upload.wikimedia.org/wikipedia/commons/9/97/OQ_logo.png"
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.image(logo_url, width=120)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='banner'><h1 style='margin:0'>PIQuick — Industrial Risk Dashboard (OQBI Oman)</h1></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Enter daily readings. Values will show visual status emoji.</p>", unsafe_allow_html=True)

st.divider()

# ----------------------------
# Tabs
# ----------------------------
tab_input, tab_results, tab_charts = st.tabs(["📝 Input", "📋 Results", "📊 Charts & Export"])

days = 5  # 5-day example

# ----------------------------
# Utility Functions
# ----------------------------
def get_emoji(value, param):
    """Return emoji based on value thresholds"""
    if param == "Pressure":
        if value > 11: return "🔥"
        elif value > 10: return "⚠️"
        else: return "✅"
    if param == "Temperature":
        if value > 75: return "🔥"
        elif value > 65: return "⚠️"
        else: return "✅"
    if param == "Flow":
        if value > 500: return "⚠️"
        else: return "✅"
    if param == "Vibration":
        if value > 70: return "🔥"
        elif value > 60: return "⚠️"
        else: return "✅"
    if param == "Oil Condition":
        if value > 5: return "🔥"
        elif value > 3: return "⚠️"
        else: return "✅"
    if param == "Chemical Conc.":
        if value > 10: return "🔥"
        elif value > 7: return "⚠️"
        else: return "✅"
    if param == "Energy":
        if value > 150: return "🔥"
        elif value > 120: return "⚠️"
        else: return "✅"
    if param == "Emissions":
        if value > 100: return "🔥"
        elif value > 80: return "⚠️"
        else: return "✅"
    return "✅"

def classify_risk(p, t, f, v, oil, chem, energy, em, alert):
    if alert == "Yes" or t > 75 or p > 11 or v > 70 or oil > 5 or chem > 10 or energy > 150 or em > 100:
        return "High"
    elif t > 65 or p > 10 or v > 60 or oil > 3 or chem > 7 or energy > 120 or em > 80:
        return "Medium"
    else:
        return "Low"

# ----------------------------
# INPUT TAB
# ----------------------------
with tab_input:
    st.header("Input Data (sections)")
    
    core_values = {"Pressure": [], "Temperature": [], "Flow": []}
    vib_values = []
    oil_values = []
    chem_values = []
    energy_values = []
    emis_values = []
    alerts = []

    # Core Process
    st.subheader("Core Process Parameters")
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    for i in range(days):
        st.markdown(f"**Day {i+1}**")
        p = st.number_input(f"Pressure (bar) — Day {i+1}", value=10.0, step=0.1, key=f"p_{i}")
        st.markdown(f"<span class='emoji'>{get_emoji(p,'Pressure')}</span>", unsafe_allow_html=True)
        t = st.number_input(f"Temperature (°C) — Day {i+1}", value=65.0, step=0.1, key=f"t_{i}")
        st.markdown(f"<span class='emoji'>{get_emoji(t,'Temperature')}</span>", unsafe_allow_html=True)
        f = st.number_input(f"Flow (L/min) — Day {i+1}", value=200.0, step=1, key=f"f_{i}")
        st.markdown(f"<span class='emoji'>{get_emoji(f,'Flow')}</span>", unsafe_allow_html=True)
        core_values["Pressure"].append(p)
        core_values["Temperature"].append(t)
        core_values["Flow"].append(f)
        st.markdown("---")
    st.markdown("</div>", unsafe_allow_html=True)

    # Mechanical
    st.subheader("Mechanical Parameters")
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    for i in range(days):
        v = st.number_input(f"Vibration (Hz) — Day {i+1}", value=50.0, step=0.1, key=f"v_{i}")
        st.markdown(f"<span class='emoji'>{get_emoji(v,'Vibration')}</span>", unsafe_allow_html=True)
        vib_values.append(v)
    st.markdown("</div>", unsafe_allow_html=True)

    # Oil & Chemical
    st.subheader("Oil & Chemical Parameters")
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    for i in range(days):
        oil = st.number_input(f"Oil Condition (index) — Day {i+1}", value=2.0, step=0.1, key=f"oil_{i}")
        st.markdown(f"<span class='emoji'>{get_emoji(oil,'Oil Condition')}</span>", unsafe_allow_html=True)
        chem = st.number_input(f"Chemical Conc. (%) — Day {i+1}", value=5.0, step=0.1, key=f"chem_{i}")
        st.markdown(f"<span class='emoji'>{get_emoji(chem,'Chemical Conc.')}</span>", unsafe_allow_html=True)
        oil_values.append(oil)
        chem_values.append(chem)
    st.markdown("</div>", unsafe_allow_html=True)

    # Energy & Environment
    st.subheader("Energy & Environment")
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    for i in range(days):
        energy = st.number_input(f"Energy Consumption (kWh) — Day {i+1}", value=100.0, step=1, key=f"energy_{i}")
        st.markdown(f"<span class='emoji'>{get_emoji(energy,'Energy')}</span>", unsafe_allow_html=True)
        em = st.number_input(f"Emissions (ppm) — Day {i+1}", value=50.0, step=1, key=f"em_{i}")
        st.markdown(f"<span class='emoji'>{get_emoji(em,'Emissions')}</span>", unsafe_allow_html=True)
        energy_values.append(energy)
        emis_values.append(em)
    st.markdown("</div>", unsafe_allow_html=True)

    # Alerts
    st.subheader("Alerts / Safety Trips")
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    for i in range(days):
        alert = st.selectbox(f"Day {i+1} Alert / Trip", ["No", "Yes"], key=f"alert_{i}")
        alerts.append(alert)
    st.markdown("</div>", unsafe_allow_html=True)

    st.success("Inputs set. Switch to Results or Charts to analyze.")

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
        "Energy": energy_values,
        "Emissions": emis_values,
        "Alert": alerts
    })

    df["Risk"] = [
        classify_risk(df.loc[i, "Pressure"], df.loc[i, "Temperature"], df.loc[i, "Flow"],
                      df.loc[i, "Vibration"], df.loc[i, "Oil Condition"],
                      df.loc[i, "Chemical Concentration"], df.loc[i, "Energy"],
                      df.loc[i, "Emissions"], df.loc[i, "Alert"])
        for i in range(len(df))
    ]

    def color_risk(val):
        if val == "High":
            return "background-color: red; color: white; font-weight: bold;"
        if val == "Medium":
            return "background-color: orange; color: white; font-weight: bold;"
        return "background-color: green; color: white; font-weight: bold;"

    st.dataframe(df.style.applymap(color_risk, subset=["Risk"]), height=360)

    high = df[df["Risk"]=="High"]["Day"].tolist()
    if high:
        st.markdown(f"<div class='summary-box'><b>⚠️ High risk on:</b> {', '.join(high)}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='summary-box'>✅ No high-risk days detected.</div>", unsafe_allow_html=True)

# ----------------------------
# CHARTS & EXPORT TAB
# ----------------------------
with tab_charts:
    st.header("Charts & Export")

    fig = go.Figure()
    x = df["Day"]

    fig.add_trace(go.Scatter(x=x, y=df["Temperature"], mode="lines+markers", name="Temperature (°C)", line=dict(color='red')))
    fig.add_trace(go.Scatter(x=x, y=df["Pressure"], mode="lines+markers", name="Pressure (bar)", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=x, y=df["Flow"], mode="lines+markers", name="Flow (L/min)", line=dict(color='green')))
    fig.add_trace(go.Scatter(x=x, y=df["Vibration"], mode="lines+markers", name="Vibration (Hz)", line=dict(color='purple')))
    fig.add_trace(go.Scatter(x=x, y=df["Oil Condition"], mode="lines+markers", name="Oil Condition", line=dict(color='brown')))
    fig.add_trace(go.Scatter(x=x, y=df["Chemical Concentration"], mode="lines+markers", name="Chemical Conc.", line=dict(color='magenta')))
    fig.add_trace(go.Scatter(x=x, y=df["Energy"], mode="lines+markers", name="Energy (kWh)", line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=x, y=df["Emissions"], mode="lines+markers", name="Emissions (ppm)", line=dict(color='gray')))

    fig.update_layout(title="Interactive Process Parameter Trends",
                      xaxis_title="Day", yaxis_title="Value",
                      hovermode="x unified",
                      template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # CSV Export
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="piquick_report.csv", mime="text/csv")
