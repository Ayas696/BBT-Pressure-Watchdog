import streamlit as st
import random
import time
from datetime import datetime

# ============================================================
# INDUSTRIAL BBT PRESSURE WATCHDOG SYSTEM
# Version 1.1
# ============================================================

# -----------------------------
# OPERATING PRESSURE SETPOINTS
# -----------------------------

NORMAL_BBT_PRESSURE = 1.0       # bar
PACKAGING_PRESSURE = 1.5        # bar


# -----------------------------
# SAFETY LIMITS
# -----------------------------

CRITICAL_HIGH_PRESSURE = 3.0    # bar
CRITICAL_LOW_PRESSURE = 0.2     # bar

HIGH_DEVIATION = 0.3            # bar
LOW_DEVIATION = 0.3             # bar


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="BBT Pressure Watchdog",
    page_icon="🍺",
    layout="wide"
)


# -----------------------------
# PRESSURE STATUS FUNCTION
# -----------------------------

def evaluate_pressure(pressure, target_pressure):

    deviation = pressure - target_pressure

    # Critical safety conditions
    if pressure >= CRITICAL_HIGH_PRESSURE:
        return "CRITICAL HIGH", "🔴"

    if pressure <= CRITICAL_LOW_PRESSURE:
        return "CRITICAL LOW - IMPLOSION RISK", "🔴"

    # Operating deviation
    if deviation > HIGH_DEVIATION:
        return "HIGH PRESSURE", "🟠"

    if deviation < -LOW_DEVIATION:
        return "LOW PRESSURE", "🟡"

    return "NORMAL", "🟢"


# -----------------------------
# HEADER
# -----------------------------

st.title("🍺 Industrial BBT Pressure Watchdog System")

st.markdown(
    """
    ### Bright Beer Tank — Pressure & Vacuum Monitoring

    Real-time monitoring of BBT top pressure against the selected
    operating setpoint.
    """
)

st.divider()


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.header("⚙️ System Controls")

tank_name = st.sidebar.text_input(
    "Tank ID",
    value="BBT-01"
)


# Operating mode

operating_mode = st.sidebar.selectbox(
    "Operating Mode",
    [
        "Normal BBT",
        "Packaging"
    ]
)


# Determine target pressure

if operating_mode == "Normal BBT":
    target_pressure = NORMAL_BBT_PRESSURE

else:
    target_pressure = PACKAGING_PRESSURE


st.sidebar.divider()

st.sidebar.subheader("Operating Setpoints")

st.sidebar.write(
    f"Normal BBT: **{NORMAL_BBT_PRESSURE:.1f} bar**"
)

st.sidebar.write(
    f"Packaging: **{PACKAGING_PRESSURE:.1f} bar**"
)


st.sidebar.divider()

st.sidebar.subheader("Safety Limits")

st.sidebar.write(
    f"Critical High: **{CRITICAL_HIGH_PRESSURE:.1f} bar**"
)

st.sidebar.write(
    f"Critical Low: **{CRITICAL_LOW_PRESSURE:.1f} bar**"
)


# -----------------------------
# SIMULATION
# -----------------------------

simulation_mode = st.sidebar.checkbox(
    "Enable pressure simulation",
    value=True
)


if simulation_mode:

    # Generate pressure around selected target
    pressure = round(
        random.uniform(
            target_pressure - 0.25,
            target_pressure + 0.25
        ),
        2
    )

else:

    pressure = target_pressure


# -----------------------------
# EVALUATE SYSTEM
# -----------------------------

status, icon = evaluate_pressure(
    pressure,
    target_pressure
)


deviation = pressure - target_pressure


# -----------------------------
# TIME
# -----------------------------

current_time = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)


# -----------------------------
# MAIN DASHBOARD
# -----------------------------

st.subheader(f"Tank: {tank_name}")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Operating Mode",
        operating_mode
    )


with col2:

    st.metric(
        "Target Pressure",
        f"{target_pressure:.2f} bar"
    )


with col3:

    st.metric(
        "Actual Pressure",
        f"{pressure:.2f} bar"
    )


with col4:

    st.metric(
        "Deviation",
        f"{deviation:+.2f} bar"
    )


st.divider()


# -----------------------------
# SYSTEM STATUS
# -----------------------------

st.subheader("System Status")


if status == "NORMAL":

    st.success(
        f"{icon} NORMAL — BBT pressure is within the "
        f"acceptable operating range."
    )


elif status == "HIGH PRESSURE":

    st.warning(
        f"{icon} HIGH PRESSURE — Pressure is above the "
        f"expected operating range."
    )


elif status == "LOW PRESSURE":

    st.warning(
        f"{icon} LOW PRESSURE — Pressure is below the "
        f"expected operating range."
    )


elif status == "CRITICAL HIGH":

    st.error(
        f"{icon} CRITICAL HIGH PRESSURE — "
        f"Immediate investigation required."
    )


elif status == "CRITICAL LOW - IMPLOSION RISK":

    st.error(
        f"{icon} CRITICAL LOW PRESSURE — "
        f"VACUUM / IMPLOSION RISK!"
    )


# -----------------------------
# PRESSURE VISUALISATION
# -----------------------------

st.divider()

st.subheader("Pressure Monitoring")


# Display pressure relative to 3 bar safety limit

gauge_value = min(
    max(pressure / CRITICAL_HIGH_PRESSURE, 0.0),
    1.0
)

st.progress(gauge_value)


st.write(
    f"**Actual:** {pressure:.2f} bar"
)

st.write(
    f"**Target:** {target_pressure:.2f} bar"
)

st.write(
    f"**Critical high:** {CRITICAL_HIGH_PRESSURE:.2f} bar"
)

st.write(
    f"**Critical low:** {CRITICAL_LOW_PRESSURE:.2f} bar"
)


# -----------------------------
# OPERATING INFORMATION
# -----------------------------

st.divider()

st.subheader("Operating Information")

info1, info2 = st.columns(2)


with info1:

    st.markdown(
        f"""
        ### Normal BBT

        **Top pressure setpoint: {NORMAL_BBT_PRESSURE:.1f} bar**

        Used when the BBT is operating under normal conditions.
        """
    )


with info2:

    st.markdown(
        f"""
        ### Packaging

        **Top pressure setpoint: {PACKAGING_PRESSURE:.1f} bar**

        Used when the BBT is supplying beer to packaging.
        """
    )


# -----------------------------
# SAFETY MONITORING
# -----------------------------

st.divider()

st.subheader("🛡️ Safety Monitoring")

safety1, safety2, safety3 = st.columns(3)


with safety1:

    st.info(
        "NORMAL BBT\n\n"
        "Target pressure: 1.0 bar"
    )


with safety2:

    st.info(
        "PACKAGING\n\n"
        "Target pressure: 1.5 bar"
    )


with safety3:

    st.warning(
        "VACUUM PROTECTION\n\n"
        "Critical low: 0.2 bar"
    )


# -----------------------------
# UPDATE
# -----------------------------

st.caption(
    f"Last system update: {current_time}"
)


# -----------------------------
# AUTOMATIC REFRESH
# -----------------------------

if simulation_mode:

    time.sleep(1)

    st.rerun()
