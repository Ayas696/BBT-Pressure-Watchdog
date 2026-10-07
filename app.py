```python
import streamlit as st
import random
import time
from datetime import datetime

# ============================================================
# INDUSTRIAL BBT SCADA SYSTEM
# VERSION 3.0
# PROCESS MIMIC + ALARM MANAGEMENT
# ============================================================

# ============================================================
# ENGINEERING SETPOINTS
# ============================================================

NORMAL_BBT_PRESSURE = 1.0
PACKAGING_PRESSURE = 1.5

CRITICAL_HIGH_PRESSURE = 3.0
CRITICAL_LOW_PRESSURE = 0.2

HIGH_WARNING_DEVIATION = 0.30
LOW_WARNING_DEVIATION = 0.30

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
# SESSION STATE
# ============================================================

if "bbt_data" not in st.session_state:

    st.session_state.bbt_data = {}

    for i in range(1, NUMBER_OF_BBTS + 1):

        tank_id = f"BBT-{i:02d}"

        mode = random.choice(
            ["Normal BBT", "Normal BBT", "Packaging"]
        )

        target = (
            NORMAL_BBT_PRESSURE
            if mode == "Normal BBT"
            else PACKAGING_PRESSURE
        )

        pressure = round(
            random.uniform(
                target - 0.10,
                target + 0.10
            ),
            2
        )

        st.session_state.bbt_data[tank_id] = {
            "pressure": pressure,
            "target": target,
            "mode": mode,
            "level": random.randint(55, 90),
            "status": "NORMAL",
            "alarm": False,
            "alarm_message": "",
            "last_status": "NORMAL",
            "valve_open": True,
            "flow": True,
            "last_update": datetime.now()
        }


if "alarm_history" not in st.session_state:
    st.session_state.alarm_history = []


# ============================================================
# STATUS ENGINE
# ============================================================

def evaluate_pressure(pressure, target):

    deviation = pressure - target

    if pressure >= CRITICAL_HIGH_PRESSURE:
        return "CRITICAL HIGH", "🔴"

    if pressure <= CRITICAL_LOW_PRESSURE:
        return "CRITICAL LOW", "🔴"

    if deviation >= HIGH_WARNING_DEVIATION:
        return "HIGH WARNING", "🟠"

    if deviation <= -LOW_WARNING_DEVIATION:
        return "LOW WARNING", "🟡"

    return "NORMAL", "🟢"


# ============================================================
# ALARM MESSAGE
# ============================================================

def get_alarm_message(tank_id, pressure, target, status):

    if status == "CRITICAL HIGH":

        return (
            f"{tank_id}: CRITICAL HIGH PRESSURE — "
            f"{pressure:.2f} bar. "
            f"Investigate pressure-control condition and "
            f"follow approved site SOP."
        )

    if status == "CRITICAL LOW":

        return (
            f"{tank_id}: CRITICAL LOW PRESSURE — "
            f"{pressure:.2f} bar. "
            f"Potential vacuum/implosion hazard. "
            f"Verify gas supply, vent path and vacuum protection."
        )

    if status == "HIGH WARNING":

        return (
            f"{tank_id}: HIGH PRESSURE WARNING — "
            f"{pressure:.2f} bar. "
            f"Pressure is significantly above the "
            f"{target:.2f} bar operating target."
        )

    if status == "LOW WARNING":

        return (
            f"{tank_id}: LOW PRESSURE WARNING — "
            f"{pressure:.2f} bar. "
            f"Pressure is significantly below the "
            f"{target:.2f} bar operating target."
        )

    return ""


# ============================================================
# ALARM HISTORY
# ============================================================

def record_alarm(tank_id, status, pressure):

    if status == "NORMAL":
        return

    event = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "tank": tank_id,
        "status": status,
        "pressure": pressure
    }

    # Prevent excessive duplicate history
    if len(st.session_state.alarm_history) == 0:

        st.session_state.alarm_history.insert(
            0,
            event
        )

    else:

        last = st.session_state.alarm_history[0]

        if not (
            last["tank"] == tank_id
            and last["status"] == status
        ):

            st.session_state.alarm_history.insert(
                0,
                event
            )

    st.session_state.alarm_history = (
        st.session_state.alarm_history[:30]
    )


# ============================================================
# PRESSURE SIMULATION
# ============================================================

def simulate_pressure(data):

    target = data["target"]
    current = data["pressure"]

    movement = random.uniform(
        -0.035,
        0.035
    )

    new_pressure = current + movement

    # Return gradually toward operating target
    if new_pressure > target + 0.20:

        new_pressure -= random.uniform(
            0.01,
            0.04
        )

    if new_pressure < target - 0.20:

        new_pressure += random.uniform(
            0.01,
            0.04
        )

    return round(
        max(0.0, new_pressure),
        2
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🍺 BBT SCADA")

st.sidebar.subheader("Navigation")

page = st.sidebar.radio(
    "Select screen",
    [
        "SCADA Overview",
        "BBT Detail",
        "Alarms & Events"
    ]
)


st.sidebar.divider()

st.sidebar.subheader("Simulation Controls")

simulation = st.sidebar.checkbox(
    "Automatic simulation",
    value=True
)


selected_simulation_tank = st.sidebar.selectbox(
    "Test tank",
    list(st.session_state.bbt_data.keys())
)


st.sidebar.markdown(
    "### Fault Injection"
)


if st.sidebar.button(
    "🔴 Create High Pressure"
):

    st.session_state.bbt_data[
        selected_simulation_tank
    ]["pressure"] = 3.10


if st.sidebar.button(
    "🔴 Create Vacuum Condition"
):

    st.session_state.bbt_data[
        selected_simulation_tank
    ]["pressure"] = 0.15


if st.sidebar.button(
    "🟢 Return to Normal"
):

    data = st.session_state.bbt_data[
        selected_simulation_tank
    ]

    data["pressure"] = data["target"]


st.sidebar.divider()

st.sidebar.subheader(
    "Engineering Setpoints"
)

st.sidebar.write(
    f"Normal BBT: **{NORMAL_BBT_PRESSURE:.1f} bar**"
)

st.sidebar.write(
    f"Packaging: **{PACKAGING_PRESSURE:.1f} bar**"
)

st.sidebar.write(
    f"Critical High: **{CRITICAL_HIGH_PRESSURE:.1f} bar**"
)

st.sidebar.write(
    f"Critical Low: **{CRITICAL_LOW_PRESSURE:.1f} bar**"
)


# ============================================================
# UPDATE PROCESS
# ============================================================

for tank_id, data in st.session_state.bbt_data.items():

    # Automatic simulation
    if simulation:

        data["pressure"] = simulate_pressure(data)

    status, icon = evaluate_pressure(
        data["pressure"],
        data["target"]
    )

    # Detect status change
    if status != data["last_status"]:

        if status != "NORMAL":

            record_alarm(
                tank_id,
                status,
                data["pressure"]
            )

        data["last_status"] = status

    data["status"] = status
    data["icon"] = icon
    data["alarm"] = status in [
        "CRITICAL HIGH",
        "CRITICAL LOW"
    ]

    data["alarm_message"] = get_alarm_message(
        tank_id,
        data["pressure"],
        data["target"],
        status
    )

    data["last_update"] = datetime.now()


# ============================================================
# HEADER
# ============================================================

st.title(
    "🍺 BRIGHT BEER TANK SCADA"
)

st.caption(
    "BBT Area Process Supervision and Alarm Monitoring"
)


# ============================================================
# SYSTEM STATUS BAR
# ============================================================

critical_count = sum(
    1
    for d in st.session_state.bbt_data.values()
    if d["status"] in [
        "CRITICAL HIGH",
        "CRITICAL LOW"
    ]
)

warning_count = sum(
    1
    for d in st.session_state.bbt_data.values()
    if d["status"] in [
        "HIGH WARNING",
        "LOW WARNING"
    ]
)


status_col1, status_col2, status_col3 = st.columns(3)


with status_col1:

    if critical_count > 0:

        st.error(
            f"🔴 SYSTEM ALARM — "
            f"{critical_count} CRITICAL"
        )

    else:

        st.success(
            "🟢 SYSTEM HEALTHY"
        )


with status_col2:

    if warning_count > 0:

        st.warning(
            f"🟡 {warning_count} WARNING(S)"
        )

    else:

        st.info(
            "🟢 NO WARNINGS"
        )


with status_col3:

    st.info(
        f"BBTs ONLINE: {NUMBER_OF_BBTS}"
    )


# ============================================================
# SCADA OVERVIEW
# ============================================================

if page == "SCADA Overview":

    st.header(
        "Process Mimic — BBT Area"
    )

    # --------------------------------------------------------
    # ALARM BANNER
    # --------------------------------------------------------

    critical_tanks = [
        (tank_id, data)
        for tank_id, data
        in st.session_state.bbt_data.items()
        if data["alarm"]
    ]

    if critical_tanks:

        for tank_id, data in critical_tanks:

            st.error(
                f"🚨 {data['alarm_message']}"
            )


    # --------------------------------------------------------
    # PROCESS GRAPHIC
    # --------------------------------------------------------

    st.subheader(
        "BBT Process Area"
    )

    svg_width = 1200
    svg_height = 500

    svg_parts = []

    svg_parts.append(
        f"""
        <svg
            width="100%"
            viewBox="0 0 {svg_width} {svg_height}"
            xmlns="http://www.w3.org/2000/svg"
        >

        <rect
            x="0"
            y="0"
            width="1200"
            height="500"
            fill="#101820"
        />

        <text
            x="600"
            y="35"
            text-anchor="middle"
            fill="white"
            font-size="24"
            font-family="Arial"
            font-weight="bold"
        >
            BBT AREA — PROCESS MIMIC
        </text>

        <!-- MAIN BEER HEADER -->

        <line
            x1="80"
            y1="420"
            x2="1120"
            y2="420"
            stroke="#58b7d8"
            stroke-width="8"
        />

        <text
            x="600"
            y="455"
            text-anchor="middle"
            fill="white"
            font-size="16"
            font-family="Arial"
        >
            BRIGHT BEER / PACKAGING HEADER
        </text>
        """
    )

    tanks = list(
        st.session_state.bbt_data.keys()
    )

    positions = [
        (120, 100),
        (390, 100),
        (660, 100),
        (930, 100),
        (120, 285),
        (390, 285),
        (660, 285),
        (930, 285)
    ]

    for index, tank_id in enumerate(tanks):

        data = st.session_state.bbt_data[tank_id]

        x, y = positions[index]

        pressure = data["pressure"]
        level = data["level"]
        status = data["status"]

        # Status graphic colour
        if status == "NORMAL":
            status_colour = "#20c997"

        elif status in [
            "HIGH WARNING",
            "LOW WARNING"
        ]:
            status_colour = "#ffc107"

        else:
            status_colour = "#ff3b30"

        # Tank dimensions
        tank_x = x
        tank_y = y
        tank_w = 120
        tank_h = 110

        # Level
        liquid_height = (
            tank_h - 15
        ) * level / 100

        liquid_y = (
            tank_y
            + tank_h
            - liquid_height
        )

        # Tank
        svg_parts.append(
            f"""
            <!-- BBT {tank_id} -->

            <ellipse
                cx="{tank_x + tank_w / 2}"
                cy="{tank_y}"
                rx="60"
                ry="14"
                fill="#25313a"
                stroke="{status_colour}"
                stroke-width="3"
            />

            <rect
                x="{tank_x}"
                y="{tank_y}"
                width="{tank_w}"
                height="{tank_h}"
                fill="#18242c"
                stroke="{status_colour}"
                stroke-width="3"
            />

            <ellipse
                cx="{tank_x + tank_w / 2}"
                cy="{tank_y + tank_h}"
                rx="60"
                ry="14"
                fill="#18242c"
                stroke="{status_colour}"
                stroke-width="3"
            />

            <!-- Beer -->

            <rect
                x="{tank_x + 3}"
                y="{liquid_y}"
                width="{tank_w - 6}"
                height="{liquid_height}"
                fill="#d99b29"
                opacity="0.85"
            />

            <!-- Tank Label -->

            <text
                x="{tank_x + tank_w / 2}"
                y="{tank_y + 35}"
                text-anchor="middle"
                fill="white"
                font-size="15"
                font-family="Arial"
                font-weight="bold"
            >
                {tank_id}
            </text>

            <!-- Pressure -->

            <text
                x="{tank_x + tank_w / 2}"
                y="{tank_y + 60}"
                text-anchor="middle"
                fill="white"
                font-size="17"
                font-family="Arial"
                font-weight="bold"
            >
                {pressure:.2f} bar
            </text>

            <!-- Mode -->

            <text
                x="{tank_x + tank_w / 2}"
                y="{tank_y + 82}"
                text-anchor="middle"
                fill="#d0d7dc"
                font-size="11"
                font-family="Arial"
            >
                {data["mode"]}
            </text>

            <!-- Status lamp -->

            <circle
                cx="{tank_x + tank_w / 2}"
                cy="{tank_y + 103}"
                r="6"
                fill="{status_colour}"
            />

            <!-- Pressure transmitter -->

            <circle
                cx="{tank_x + tank_w / 2}"
                cy="{tank_y - 25}"
                r="12"
                fill="#202b33"
                stroke="{status_colour}"
                stroke-width="2"
            />

            <text
                x="{tank_x + tank_w / 2}"
                y="{tank_y - 21}"
                text-anchor="middle"
                fill="white"
                font-size="8"
                font-family="Arial"
            >
                PT
            </text>

            <!-- Pipe -->

            <line
                x1="{tank_x + tank_w / 2}"
                y1="{tank_y + tank_h + 14}"
                x2="{tank_x + tank_w / 2}"
                y2="420"
                stroke="#58b7d8"
                stroke-width="5"
            />

            <!-- Valve -->

            <polygon
                points="
                {tank_x + tank_w / 2 - 9},{tank_y + tank_h + 35}
                {tank_x + tank_w / 2},{tank_y + tank_h + 25}
                {tank_x + tank_w / 2 + 9},{tank_y + tank_h + 35}
                {tank_x + tank_w / 2},{tank_y + tank_h + 45}
                "
                fill="#68757d"
                stroke="white"
                stroke-width="1"
            />

            <!-- Flow arrow -->

            <polygon
                points="
                {tank_x + tank_w / 2 - 5},405
                {tank_x + tank_w / 2 + 7},405
                {tank_x + tank_w / 2 + 1},414
                "
                fill="#58b7d8"
            />
            """
        )

    svg_parts.append(
        """
        </svg>
        """
    )

    svg_code = "".join(svg_parts)

    st.components.v1.html(
        svg_code,
        height=520,
        scrolling=False
    )


    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    st.markdown(
        """
        **SCADA Legend**

        🟢 Normal &nbsp;&nbsp;
        🟡 Low/High Warning &nbsp;&nbsp;
        🟠 High Warning &nbsp;&nbsp;
        🔴 Critical Alarm &nbsp;&nbsp;
        🔵 Product Flow
        """
    )


# ============================================================
# BBT DETAIL
# ============================================================

elif page == "BBT Detail":

    st.header(
        "BBT Detailed Process View"
    )

    selected_tank = st.selectbox(
        "Select Bright Beer Tank",
        list(
            st.session_state.bbt_data.keys()
        )
    )

    data = st.session_state.bbt_data[
        selected_tank
    ]

    st.divider()

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
            "Level",
            f"{data['level']} %"
        )

    with col4:
        st.metric(
            "Mode",
            data["mode"]
        )

    st.divider()

    # Alarm
    if data["status"] == "NORMAL":

        st.success(
            "🟢 NORMAL — "
            "Pressure is within the operating range."
        )

    elif data["status"] == "HIGH WARNING":

        st.warning(
            f"🟠 HIGH PRESSURE WARNING\n\n"
            f"{data['alarm_message']}\n\n"
            f"OPERATOR PROMPT: Check pressure control "
            f"and verify the approved operating procedure."
        )

    elif data["status"] == "LOW WARNING":

        st.warning(
            f"🟡 LOW PRESSURE WARNING\n\n"
            f"{data['alarm_message']}\n\n"
            f"OPERATOR PROMPT: Verify gas supply, "
            f"pressure control and operating conditions."
        )

    elif data["status"] == "CRITICAL HIGH":

        st.error(
            f"🚨 CRITICAL HIGH PRESSURE\n\n"
            f"{data['alarm_message']}\n\n"
            f"OPERATOR PROMPT: Investigate immediately "
            f"and follow the site's approved emergency/SOP response."
        )

    elif data["status"] == "CRITICAL LOW":

        st.error(
            f"🚨 CRITICAL LOW PRESSURE — VACUUM RISK\n\n"
            f"{data['alarm_message']}\n\n"
            f"OPERATOR PROMPT: Treat as a potential "
            f"vacuum/implosion hazard and follow the site's "
            f"approved emergency/SOP response."
        )

    st.divider()

    # Pressure indicator
    st.subheader("Pressure Transmitter — PT")

    gauge = min(
        max(
            data["pressure"]
            / CRITICAL_HIGH_PRESSURE,
            0
        ),
        1
    )

    st.progress(gauge)

    st.write(
        f"Current pressure: **{data['pressure']:.2f} bar**"
    )

    st.write(
        f"Normal BBT target: **{NORMAL_BBT_PRESSURE:.1f} bar**"
    )

    st.write(
        f"Packaging target: **{PACKAGING_PRESSURE:.1f} bar**"
    )

    st.write(
        f"Critical high: **{CRITICAL_HIGH_PRESSURE:.1f} bar**"
    )

    st.write(
        f"Critical low: **{CRITICAL_LOW_PRESSURE:.1f} bar**"
    )

    st.divider()

    # Process equipment
    st.subheader("Process Equipment")

    equipment_col1, equipment_col2, equipment_col3 = st.columns(3)

    with equipment_col1:

        if data["valve_open"]:

            st.success(
                "🟢 Beer Outlet Valve\n\nOPEN"
            )

        else:

            st.error(
                "🔴 Beer Outlet Valve\n\nCLOSED"
            )

    with equipment_col2:

        if data["flow"]:

            st.success(
                "🔵 Product Flow\n\nFLOWING"
            )

        else:

            st.info(
                "⚪ Product Flow\n\nNO FLOW"
            )

    with equipment_col3:

        st.info(
            f"Tank Level\n\n{data['level']} %"
        )


# ============================================================
# ALARMS & EVENTS
# ============================================================

elif page == "Alarms & Events":

    st.header(
        "🚨 Alarm & Event Management"
    )

    active = []

    for tank_id, data in (
        st.session_state.bbt_data.items()
    ):

        if data["status"] != "NORMAL":

            active.append(
                (tank_id, data)
            )


    st.subheader(
        "Active Alarms"
    )

    if not active:

        st.success(
            "🟢 No active alarms."
        )

    else:

        for tank_id, data in active:

            if data["status"] in [
                "CRITICAL HIGH",
                "CRITICAL LOW"
            ]:

                st.error(
                    f"🔴 {tank_id} | "
                    f"{data['status']} | "
                    f"{data['pressure']:.2f} bar"
                )

            else:

                st.warning(
                    f"🟡 {tank_id} | "
                    f"{data['status']} | "
                    f"{data['pressure']:.2f} bar"
                )


    st.divider()

    st.subheader(
        "Alarm History"
    )

    if not st.session_state.alarm_history:

        st.info(
            "No alarm events recorded."
        )

    else:

        for event in (
            st.session_state.alarm_history
        ):

            st.write(
                f"**{event['time']}** | "
                f"**{event['tank']}** | "
                f"{event['status']} | "
                f"{event['pressure']:.2f} bar"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "BBT SCADA System v3.0 | "
    "Simulation environment | "
    "Operating setpoints are project assumptions and "
    "must be validated against plant documentation before use."
)


# ============================================================
# AUTOMATIC UPDATE
# ============================================================

if simulation:

    time.sleep(1)

    st.rerun()
```

