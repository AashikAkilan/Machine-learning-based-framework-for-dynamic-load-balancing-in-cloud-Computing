import paramiko
import json
import threading
import time
from datetime import datetime
import subprocess

# VM Configuration
VM_CONFIG = {
    "vm1": "192.168.56.101",
    "vm2": "192.168.56.102",
    "vm3": "192.168.56.103",
}

USERNAME = "kali"
PASSWORD = "kali"

ACTIVE_VMS = ["vm1", "vm2"]  # Start with 2 VMs
metrics_data = {}

# Scaling thresholds (simulation)
CPU_SCALE_UP = 75
CPU_SCALE_DOWN = 30

# Historical CSV logging
HIST_FILE = "metrics_history.csv"

# ---- Start/Stop VMs (simulate) ----
def start_vm(vm):
    if vm not in ACTIVE_VMS:
        print(f"[SCALING] Starting {vm}")
        # subprocess.run(["VBoxManage", "startvm", vm, "--type", "headless"])
        ACTIVE_VMS.append(vm)

def stop_vm(vm):
    if vm in ACTIVE_VMS:
        print(f"[SCALING] Stopping {vm}")
        # subprocess.run(["VBoxManage", "controlvm", vm, "poweroff"])
        ACTIVE_VMS.remove(vm)

# ---- Load calculation for scaling ----
def calculate_load(data):
    return 0.5*data["cpu"] + 0.3*data["memory"] + 0.2*data["network"]

# ---- Monitor each VM via SSH ----
def monitor_vm(name, ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    while True:
        try:
            ssh.connect(ip, username=USERNAME, password=PASSWORD, timeout=10)
            stdin, stdout, stderr = ssh.exec_command("python3 /home/kali/task_monitor.py")
            for line in stdout:
                try:
                    data = json.loads(line.strip())
                    metrics_data[name] = data
                    # Append historical CSV
                    with open(HIST_FILE, "a") as f:
                        f.write(f"{datetime.now()},{name},{data['cpu']},{data['memory']},{data['network']}\n")
                except:
                    continue
        except Exception as e:
            print(f"[!] Failed to connect {name}: {e}")
        time.sleep(2)

# ---- Scaling Controller (simulate adding/removing VMs) ----
def scaling_controller():
    while True:
        if len(metrics_data) >= 2:
            loads = [calculate_load(metrics_data[vm]) for vm in ACTIVE_VMS if vm in metrics_data]
            avg_load = sum(loads) / len(loads)
            print(f"[INFO] Average Load: {avg_load:.2f}")

            if avg_load > CPU_SCALE_UP and "vm3" not in ACTIVE_VMS:
                start_vm("vm3")
            if avg_load < CPU_SCALE_DOWN and "vm3" in ACTIVE_VMS:
                stop_vm("vm3")

            # Write metrics.json for dashboard/controller
            with open("metrics.json", "w") as f:
                json.dump({
                    "metrics": metrics_data,
                    "active_vms": ACTIVE_VMS,
                    "avg_load": avg_load
                }, f)
        time.sleep(5)

# ---- Start monitoring threads ----
for vm in ACTIVE_VMS:
    threading.Thread(target=monitor_vm, args=(vm, VM_CONFIG[vm]), daemon=True).start()

threading.Thread(target=scaling_controller, daemon=True).start()

# Keep alive
while True:
    time.sleep(1)
