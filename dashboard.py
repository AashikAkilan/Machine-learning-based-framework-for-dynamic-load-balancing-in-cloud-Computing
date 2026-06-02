import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from datetime import datetime
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")

# ---- Custom CSS (Dark Gradient Background) ----
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
.metric-box {
    background-color: #111827;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("Load Balancing Monitoring Dashboard")

# ---- Load Real Metrics ----
try:
    with open("metrics.json", "r") as f:
        data = json.load(f)
    metrics = data["metrics"]
    active_vms = data["active_vms"]
    avg_load = data.get("avg_load", 0)
    selected_vm = data.get("last_selected_vm", None)
    last_reward = data.get("last_reward", None)
except:
    # fallback in case file missing
    metrics = {
        "vm1": {"cpu": 0, "memory": 0, "network": 0, "tasks": 0},
        "vm2": {"cpu": 0, "memory": 0, "network": 0, "tasks": 0},
        "vm3": {"cpu": 0, "memory": 0, "network": 0, "tasks": 0},
    }
    active_vms = ["vm1", "vm2", "vm3"]
    avg_load = 0
    selected_vm = None
    last_reward = None

# ---- Convert to DataFrame ----
df = pd.DataFrame(metrics).T

# ---- TOP ROW CHARTS ----
col1, col2 = st.columns(2)

# CPU Chart
with col1:
    fig_cpu = go.Figure()
    fig_cpu.add_trace(go.Scatter(
        y=[df.loc[vm,"cpu"] for vm in df.index],
        x=df.index,
        mode='lines+markers',
        line=dict(color='#00F5D4', width=3),
        name="CPU"
    ))
    fig_cpu.update_layout(
        title="CPU Utilization (%)",
        template="plotly_dark"
    )
    st.plotly_chart(fig_cpu, use_container_width=True)

# Memory Chart
with col2:
    fig_mem = go.Figure()
    fig_mem.add_trace(go.Scatter(
        y=[df.loc[vm,"memory"] for vm in df.index],
        x=df.index,
        mode='lines+markers',
        line=dict(color='#FFA500', width=3),
        name="Memory"
    ))
    fig_mem.update_layout(
        title="Memory Usage (%)",
        template="plotly_dark"
    )
    st.plotly_chart(fig_mem, use_container_width=True)

# ---- BOTTOM ROW CHARTS ----
col3, col4, col5 = st.columns(3)

# Network Chart
with col3:
    fig_net = go.Figure()
    fig_net.add_trace(go.Bar(
        x=df.index,
        y=df["network"],
        marker_color=['#00BFFF','#FF69B4','#32CD32']
    ))
    fig_net.update_layout(
        title="Network Traffic (Mbps)",
        template="plotly_dark"
    )
    st.plotly_chart(fig_net, use_container_width=True)

# Task Distribution
with col4:
    tasks = [metrics[vm].get("tasks", 0) for vm in active_vms]
    fig_task = go.Figure()
    fig_task.add_trace(go.Bar(
        x=active_vms,
        y=tasks,
        marker_color=['#1f77b4','#ff7f0e','#2ca02c']
    ))
    fig_task.update_layout(
        title="Task Distribution",
        template="plotly_dark"
    )
    st.plotly_chart(fig_task, use_container_width=True)

#  Decision Log
with col5:
    decision_log = data.get('decision_log', [])
    if decision_log:
        df_decision = pd.DataFrame(decision_log)
    else:
        df_decision = pd.DataFrame({
            "Time": [datetime.now().strftime("%H:%M:%S")],
            "Predicted Load": [round(avg_load, 2)],
            "Selected VM": [selected_vm if selected_vm else "N/A"],
            "Reward": [last_reward if last_reward else "N/A"]
        })
    st.subheader("Decision Log")
    st.dataframe(df_decision)
