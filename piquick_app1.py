import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="PIQuick Dashboard - OQBI Oman", layout="wide")

# ----------------------------
# Custom CSS for Background & Colors
# ----------------------------
st.markdown("""
<style>
body, .main, .block-container {
    /* Main background color for a light, professional look */
    background-color: #f0f8ff; /* Light Azure */
    color: #003366; /* Deep Blue for main text */
}
h1, h2, h3, h4 {
    /* Accent color for headers */
    color: #ff8000; /* Vibrant Orange */
    font-weight: bold;
}
.summary-card {
    /* Slightly translucent white card for summaries */
    background-color: #ffffffd0;
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
}
.stDataFrame thead th {
    /* Header background color for the table */
    background-color: #ffb366; /* Light Orange */
    color: #003366;
}
input[type=number] {
    font-weight: bold;
    border-radius: 6px;
}
/* Ensure the selectbox reflects the page colors */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #ffffff;
    border-radius: 6px;
    border: 1px solid #ccc;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Initialization and Configuration Data
# ----------------------------
if 'analyzed_days' not in st.session_state:
    st.session_state.analyzed_days = []

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

# Initialize session state data if not present
if 'params_data' not in st.session_state:
    st.session_state.params_data = {
        day: {param: (limits[param][0] + limits[param][1]) / 2 for param in params}
        for day in days
    }

# ----------------------------
# Header UI
# ----------------------------
dropdown_options = [f"{d} ✅" if d in st.session_state.analyzed_days else d for d in days]
col1, col2 = st.columns([5, 1])

with col1:
    st.markdown("<h1><span style='color:#003366;'>OQBI Oman</span> - PIQuick Risk Dashboard</h1>", unsafe_allow_html=True)
    st.write("Monitor industrial parameters, detect anomalies, and visualize trends easily.")
with col2:
    selected_day = st.selectbox("📅 Select Day", dropdown_options, key="day_selector")

selected_day_clean = selected_day.replace(" ✅", "")

# ----------------------------
# Input for Selected Day with ranges
# ----------------------------
st.markdown(f"<h3>📝 Enter Process Data for {selected_day_clean}</h3>", unsafe_allow_html=True)
st.divider()

cols = st.columns(3)
i = 0
for param, label in params.items():
    lower, upper = limits[param]
    display_label = f"{label} (Range: {lower} - {upper})"
    
    # Retrieve current value from session state
    current_value = st.session_state.params_data[selected_day_clean][param]
    
    with cols[i % 3]:
        # Input widget
        val = st.number_input(
            display_label, 
            value=current_value,
            step=1.0,
            key=f"{param}_{selected_day_clean}",
            format="%.2f"
        )
        
        # Live feedback and update session state
        is_normal = lower <= val <= upper
        
        # Explicit color choices: Green for normal, Red for risk
        color = "#008000" if is_normal else "#ff4d4d" # Dark Green vs Light Red
        font_weight = "bold" if not is_normal else "normal"
        status_icon = "🔥 High Risk" if not is_normal else "✅ Normal Range"
        
        st.markdown(f"<p style='color:{color}; font-weight:{font_weight}; margin-top:-10px; font-size: 0.9em;'>Status: {status_icon}</p>", unsafe_allow_html=True)
        
        # Update session state with the new value
        st.session_state.params_data[selected_day_clean][param] = val
        
    i += 1

st.divider()

# ----------------------------
# Analysis and Visualization Section
# ----------------------------
if st.button("Analyze and Generate Report", type="primary"):
    # Mark day as analyzed
    if selected_day_clean not in st.session_state.analyzed_days:
        st.session_state.analyzed_days.append(selected_day_clean)
        # Force a rerun to update the selectbox label
        st.rerun()

    # Combine all days into DataFrame
    df = pd.DataFrame([{ "Day": d, **st.session_state.params_data[d]} for d in days])
    
    st.subheader("📊 Full Process Data Summary")

    # Risk Classification for DataFrame Styling
    def style_cells(val, param):
        lower, upper = limits[param]
        # Check if the value is numerical before comparison
        if pd.isna(val) or not isinstance(val, (int, float)):
             return ""
        if lower <= val <= upper:
            # Green background for in-range values
            return "background-color:#ccffcc; color:#006600; font-weight:normal; text-align:center;"
        else:
            # Highlight out-of-range values in red
            return "background-color:#ff4d4d; color:white; font-weight:bold; text-align:center;"

    # Apply styling for all parameter columns
    styled_df = df.style
    for param in params.keys():
        styled_df = styled_df.applymap(lambda v: style_cells(v, param), subset=[param])

    # Display the styled dataframe
    st.dataframe(styled_df, height=300, use_container_width=True) # 

    # ----------------------------
    # Summary of Critical Events
    # ----------------------------
    summary_list = []
    for d in days:
        for param, label in params.items():
            lower, upper = limits[param]
            val = st.session_state.params_data[d][param]
            if val < lower:
                summary_list.append(f"⚠️ {label} (Value: {val:.2f}) is **below** the lower limit of {lower} on **{d}**.")
            elif val > upper:
                summary_list.append(f"🔥 {label} (Value: {val:.2f}) is **above** the upper limit of {upper} on **{d}**.")
                
    if not summary_list:
        summary_text = "✅ **System Status: Excellent.** All parameters across all days are within the normal operating range. No critical events detected."
    else:
        summary_text = "**Immediate Action Required:** The following critical events were detected across the analyzed days:\n\n- " + "\n- ".join(summary_list)

    st.markdown(f"""
    <div class='summary-card'>
    <h4>Summary of Critical Events</h4>
    <p>{summary_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ----------------------------
    # Trend Graph for all days (using Matplotlib as in original)
    # ----------------------------
    st.subheader("📈 Process Parameter Trend Analysis")
    
    # Prepare the DataFrame for plotting (set Day as index for better plotting by Matplotlib)
    plot_df = df.set_index("Day")

    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Plot each parameter
    for param, label in params.items():
        ax.plot(plot_df.index, plot_df[param], marker="o", label=label, linewidth=2)
        
        # Add limit lines for visual context (using pressure limits as a representative example)
        lower, upper = limits[param]
        ax.axhspan(lower * 0.95, lower * 1.05, color='gray', alpha=0.1, zorder=-1) # Shading around the limits
        ax.axhspan(upper * 0.95, upper * 1.05, color='gray', alpha=0.1, zorder=-1) # Shading around the limits
        
    ax.set_title("Process Parameter Trends Over 5 Days", fontsize=16, color="#003366")
    ax.set_xlabel("Day", fontsize=12)
    ax.set_ylabel("Value", fontsize=12)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)

    # ----------------------------
    # Individual Parameter Scatter/Line Charts (Enhanced View)
    # ----------------------------
    st.markdown("---")
    st.subheader("Detail View: Individual Parameter Trends")
    
    # Select which parameter to view in detail
    detail_param_label = st.selectbox("Select Parameter to View in Detail", list(params.values()))
    detail_param_key = [k for k, v in params.items() if v == detail_param_label][0]
    lower, upper = limits[detail_param_key]
    
    fig_detail, ax_detail = plt.subplots(figsize=(10, 4))
    
    # Plot the selected parameter trend
    ax_detail.plot(df["Day"], df[detail_param_key], marker="o", color="#ff8000", linewidth=3, label="Actual Value")
    
    # Add High and Low Limit lines
    ax_detail.axhline(upper, color='red', linestyle='--', label='Upper Limit')
    ax_detail.axhline(lower, color='red', linestyle='--', label='Lower Limit')
    
    ax_detail.set_title(f"Trend for {detail_param_label}", fontsize=14, color="#003366")
    ax_detail.set_xlabel("Day")
    ax_detail.set_ylabel("Value")
    ax_detail.legend(loc='best')
    ax_detail.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    st.pyplot(fig_detail)
