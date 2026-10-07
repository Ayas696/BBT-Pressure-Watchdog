import streamlit as st
import random
import time
from datetime import datetime

# ============================================================
# INDUSTRIAL BBT SCADA SYSTEM
# Version 2.0
# Bright Beer Tank Area Monitoring
# ============================================================

# ============================================================
# CONFIGURATION
# ============================================================

NORMAL_BBT_PRESSURE = 1.0
PACKAGING_PRESSURE = 1.5

CRITICAL_HIGH_PRESSURE = 3.0
CRITICAL_LOW_PRESSURE = 0.2

HIGH_DEVIATION = 0.30
LOW_DEVIATION = 0.30

NUMBER_OF_BBTS = 8


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BBT SCADA System",
    page_icon="🍺",
    layout="wide"
)


# ============================================================
# INITIALISE SESSION STATE
# ============================================================

if "bbt_data" not in st.session_state:

    st.session_state.bbt_data = {}

    for i in range(1, NUMBER_OF_BBTS + 1):

        tank_id = f"BBT-{i:02d}"

        mode = random.choice([
            "Normal BBT",
            "Normal BBT",
            "Normal BBT",
            "Packaging"
        ])

        if mode == "Normal BBT":
            target = NORMAL_BBT_PRESSURE
        else:
            target = PACKAGING_PRESSURE

        pressure = round(
            random.uniform(
                target - 0.12,
                target + 0.12
            ),
            2
        )

        st.session_state.bbt_data[tank_id] = {
            "pressure": pressure,
            "mode": mode,
            "target": target,
            "last_status": "NORMAL",
            "alarm": False,
            "last_update": datetime.now()
        }


# ============================================================
# PRESSURE STATUS
# ============================================================

def evaluate_pressure(pressure, target):

    deviation = pressure - target

    if pressure >= CRITICAL_HIGH_PRESSURE:
        return "CRITICAL HIGH", "🔴"

    if pressure <= CRITICAL_LOW_PRESSURE:
        return "CRITICAL LOW", "🔴"

    if deviation > HIGH_DEVIATION:
        return "HIGH WARNING", "🟠"

    if deviation < -LOW_DEVIATION:
        return "LOW WARNING", "🟡"

    return "NORMAL", "🟢"


# ============================================================
# SIMULATE BBT PRESSURE
# ============================================================

def update_pressure(data):

    target = data["target"]
    current = data["pressure"]

    # Small natural pressure movement
    movement = random.uniform(-0.05, 0.05)

    new_pressure = current + movement

    # Keep simulation around operating target
    if new_pressure > target + 0.25:
        new_pressure -= random.uniform(0.02, 0.08)

    if new_pressure < target - 0.25:
        new_pressure += random.uniform(0.02, 0.08)

    # Rare abnormal events for SCADA demonstration
    event_probability = random.random()

    if event_probability < 0.01:
        new_pressure = random.uniform(
            2.5,
            3.2
        )

    elif event_probability < 0.02:
        new_pressure = random.uniform(
            0.15,
            0.55
        )

    return round(
        max(0.0, new_pressure),
        2
    )


# ============================================================
# UPDATE ALL BBTs
# ============================================================

for tank_id, data in st.session_state.bbt_data.items():

    data["pressure"] = update_pressure(data)

    status, icon = evaluate_pressure(
        data["pressure"],
        data["target"]
    )

    data["status"] = status
    data["icon"] = icon
    data["last_update"] = datetime.now()

    if status in [
        "CRITICAL HIGH",
        "CRITICAL LOW"
    ]:

        data["alarm"] = True

    else:

        data["alarm"] = False


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("🍺 BBT SCADA")

st.sidebar.markdown(
    "### Navigation"
)

page = st.sidebar.radio(
    "Select View",
    [
        "SCADA Overview",
        "BBT Detail",
        "Alarms & Events"
    ]
)


st.sidebar.divider()

st.sidebar.subheader("System")

st.sidebar.success(
    "🟢 SCADA ONLINE"
)

st.sidebar.write(
    f"Monitoring: **{NUMBER_OF_BBTS} BBTs**"
)

st.sidebar.write(
    "Update rate: **1 second**"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🍺 Bright Beer Tank SCADA System"
)

st.caption(
    "Industrial BBT Pressure Monitoring & Supervision"
)


# ============================================================
# SCADA OVERVIEW
# ============================================================

if page == "SCADA Overview":

    st.header("SCADA Overview")

    # --------------------------------------------------------
    # SYSTEM SUMMARY
    # --------------------------------------------------------

    normal_count = 0
    warning_count = 0
    critical_count = 0

    for data in st.session_state.bbt_data.values():

        if data["status"] == "NORMAL":
            normal_count += 1

        elif data["status"] in [
            "HIGH WARNING",
            "LOW WARNING"
        ]:
            warning_count += 1

        else:
            critical_count += 1


    total_bbt = NUMBER_OF_BBTS


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Total BBTs",
            total_bbt
        )


    with col2:

        st.metric(
            "🟢 Normal",
            normal_count
        )


    with col3:

        st.metric(
            "🟡 Warnings",
            warning_count
        )


    with col4:

        st.metric(
            "🔴 Critical",
            critical_count
        )


    st.divider()


    # --------------------------------------------------------
    # BBT GRID
    # --------------------------------------------------------

    st.subheader("BBT Area")

    tanks = list(
        st.session_state.bbt_data.keys()
    )


    for row_start in range(
        0,
        len(tanks),
        4
    ):

        columns = st.columns(4)

        for index, tank_id in enumerate(
            tanks[row_start:row_start + 4]
        ):

            data = st.session_state.bbt_data[
                tank_id
            ]

            with columns[index]:

                st.markdown(
                    f"### {tank_id}"
                )

                st.markdown(
                    f"## {data['icon']} "
                    f"{data['pressure']:.2f} bar"
                )

                st.write(
                    f"Mode: **{data['mode']}**"
                )

                st.write(
                    f"Target: **{data['target']:.2f} bar**"
                )

                st.write(
                    f"Status: **{data['status']}**"
                )

                if data["alarm"]:

                    st.error(
                        "ALARM ACTIVE"
                    )

                elif data["status"] != "NORMAL":

                    st.warning(
                        "WARNING"
                    )

                else:

                    st.success(
                        "NORMAL"
                    )

                st.divider()


    # --------------------------------------------------------
    # PRESSURE TABLE
    # --------------------------------------------------------

    st.subheader("Pressure Summary")

    for tank_id, data in st.session_state.bbt_data.items():

        deviation = (
            data["pressure"]
            - data["target"]
        )

        st.write(
            f"**{tank_id}** | "
            f"{data['pressure']:.2f} bar | "
            f"Target: {data['target']:.2f} bar | "
            f"Deviation: {deviation:+.2f} bar | "
            f"{data['icon']} {data['status']}"
        )


# ============================================================
# BBT DETAIL
# ============================================================

elif page == "BBT Detail":

    st.header("BBT Detailed View")


    selected_tank = st.selectbox(
        "Select BBT",
        list(
            st.session_state.bbt_data.keys()
        )
    )


    data = st.session_state.bbt_data[
        selected_tank
    ]


    st.divider()


    # --------------------------------------------------------
    # TANK INFORMATION
    # --------------------------------------------------------

    st.subheader(
        f"{selected_tank} — Detailed Monitoring"
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Pressure",
            f"{data['pressure']:.2f} bar"
        )


    with col2:

        st.metric(
            "Target",
            f"{data['target']:.2f} bar"
        )


    with col3:

        st.metric(
            "Operating Mode",
            data["mode"]
        )


    with col4:

        st.metric(
            "Status",
            data["status"]
        )


    st.divider()


    # --------------------------------------------------------
    # PRESSURE GAUGE
    # --------------------------------------------------------

    st.subheader(
        "Pressure Level"
    )


    gauge = min(
        max(
            data["pressure"]
            / CRITICAL_HIGH_PRESSURE,
            0.0
        ),
        1.0
    )


    st.progress(gauge)


    st.write(
        f"Current pressure: "
        f"**{data['pressure']:.2f} bar**"
    )


    st.write(
        f"Operating target: "
        f"**{data['target']:.2f} bar**"
    )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if data["status"] == "NORMAL":

        st.success(
            "🟢 BBT operating normally."
        )

    elif data["status"] == "HIGH WARNING":

        st.warning(
            "🟠 Pressure is above the expected operating range."
        )

    elif data["status"] == "LOW WARNING":

        st.warning(
            "🟡 Pressure is below the expected operating range."
        )

    elif data["status"] == "CRITICAL HIGH":

        st.error(
            "🔴 CRITICAL HIGH PRESSURE!"
        )

    elif data["status"] == "CRITICAL LOW":

        st.error(
            "🔴 CRITICAL LOW PRESSURE — POSSIBLE IMPLOSION RISK!"
        )


    st.divider()


    # --------------------------------------------------------
    # OPERATING SETPOINTS
    # --------------------------------------------------------

    st.subheader(
        "Operating Setpoints"
    )


    set_col1, set_col2, set_col3 = st.columns(3)


    with set_col1:

        st.info(
            f"Normal BBT\n\n"
            f"{NORMAL_BBT_PRESSURE:.1f} bar"
        )


    with set_col2:

        st.info(
            f"Packaging\n\n"
            f"{PACKAGING_PRESSURE:.1f} bar"
        )


    with set_col3:

        st.warning(
            f"Critical Low\n\n"
            f"{CRITICAL_LOW_PRESSURE:.1f} bar"
        )


# ============================================================
# ALARMS & EVENTS
# ============================================================

elif page == "Alarms & Events":

    st.header(
        "🚨 Alarms & Events"
    )


    active_alarms = []


    for tank_id, data in (
        st.session_state.bbt_data.items()
    ):

        if data["alarm"]:

            active_alarms.append(
                (
                    tank_id,
                    data
                )
            )


    # --------------------------------------------------------
    # ACTIVE ALARMS
    # --------------------------------------------------------

    st.subheader(
        "Active Alarms"
    )


    if len(active_alarms) == 0:

        st.success(
            "🟢 No active critical alarms."
        )

    else:

        for tank_id, data in active_alarms:

            st.error(
                f"🔴 {tank_id} — "
                f"{data['status']} — "
                f"{data['pressure']:.2f} bar"
            )


    st.divider()


    # --------------------------------------------------------
    # CURRENT BBT STATUS
    # --------------------------------------------------------

    st.subheader(
        "Current BBT Status"
    )


    for tank_id, data in (
        st.session_state.bbt_data.items()
    ):

        st.write(
            f"{data['icon']} "
            f"**{tank_id}** | "
            f"{data['pressure']:.2f} bar | "
            f"{data['mode']} | "
            f"{data['status']}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "BBT SCADA System | "
    "Pressure monitoring simulation | "
    "Version 2.0"
)


# ============================================================
# AUTOMATIC REFRESH
# ============================================================

time.sleep(1)

st.rerun()
