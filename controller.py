'''import json
import time
import random
import os
from task_manager import run_task
from predictor import predict_load
from dqn_agent import select_vm

# -------------------------------
# CONFIG
# -------------------------------
DEFAULT_VMS = ["vm1", "vm2", "vm3"]

VM_CAPACITY = 100
SLA_THRESHOLD = 0.80

TASKS = [
    "tasks/cpu_task.py",
    "tasks/memory_task.py",
    "tasks/network_task.py"
]

# System counters
total_tasks = 0
successful_tasks = 0
sla_violations = 0


# -------------------------------
# SAVE METRICS FUNCTION
# -------------------------------
def save_live_metrics(metrics, active_vms, avg_load,
                      last_selected_vm=None, last_reward=None):

    if os.path.exists("metrics.json"):
        with open("metrics.json", "r") as f:
            data = json.load(f)
    else:
        data = {}

    data["metrics"] = metrics
    data["active_vms"] = active_vms
    data["avg_load"] = avg_load
    data["total_tasks"] = total_tasks
    data["successful_tasks"] = successful_tasks
    data["sla_violations"] = sla_violations

    if "decision_log" not in data:
        data["decision_log"] = []

    if last_selected_vm is not None and last_reward is not None:
        data["decision_log"].append({
            "time": time.strftime("%H:%M:%S"),
            "selected_vm": last_selected_vm,
            "reward": round(last_reward, 2),
            "predicted_load": round(avg_load, 2)
        })

    with open("metrics.json", "w") as f:
        json.dump(data, f, indent=4)


print("[INFO] Starting Adaptive Load Balancer Controller...")


# -------------------------------
# INITIALIZE METRICS.JSON
# -------------------------------
if not os.path.exists("metrics.json"):

    print("[INFO] Creating initial metrics.json...")

    default_metrics = {
        vm: {
            # Modified CPU range (Realistic)
            "cpu": random.randint(20, 85),
            "memory": random.randint(20, 60),
            "network": random.randint(100, 300),
            "tasks": 0
        }
        for vm in DEFAULT_VMS
    }

    save_live_metrics(default_metrics, DEFAULT_VMS, avg_load=0)


# -------------------------------
# MAIN LOOP
# -------------------------------
while True:

    try:
        with open("metrics.json", "r") as f:
            data = json.load(f)

        metrics = data.get("metrics", {})
        active_vms = data.get("active_vms", DEFAULT_VMS)

    except Exception as e:
        print("[ERROR] Reading metrics.json failed:", e)
        time.sleep(2)
        continue

    if not active_vms:
        time.sleep(2)
        continue

    # -------------------------------
    # PREDICT LOAD FOR EACH VM
    # -------------------------------
    predictions = {}

    for vm in active_vms:
        if vm in metrics:
            predictions[vm] = predict_load(metrics[vm])
        else:
            predictions[vm] = 0

    # -------------------------------
    # SELECT VM USING DQN
    # -------------------------------
    selected_vm, last_reward = select_vm(predictions, metrics, active_vms)

    # -------------------------------
    # ASSIGN RANDOM TASK
    # -------------------------------
    task = random.choice(TASKS)

    print(f"[TASK] {task} → {selected_vm} "
          f"(Predicted Load: {predictions[selected_vm]:.2f})")

    run_task(selected_vm, task)

    # -------------------------------
    # UPDATE SYSTEM METRICS
    # -------------------------------
    total_tasks += 1

    vm_cpu = metrics[selected_vm]["cpu"]
    vm_capacity = VM_CAPACITY

    #  ADAPTIVE SLA LOGIC
    sla_threshold = SLA_THRESHOLD * vm_capacity   # 70%

    if vm_cpu >= sla_threshold:
        sla_violations += 1
        print(f"[SLA] Violation on {selected_vm} (CPU={vm_cpu}%)")
    else:
        successful_tasks += 1

    # Update task counter
    if "tasks" not in metrics[selected_vm]:
        metrics[selected_vm]["tasks"] = 0

    metrics[selected_vm]["tasks"] += 1

    # Update average predicted load
    avg_load = sum(predictions.values()) / len(predictions)

    # Save everything
    save_live_metrics(metrics, active_vms,
                      avg_load, selected_vm, last_reward)

    # Increased interval (Less heat)
    time.sleep(15)
'''
import json
import time
import random
import os
from task_manager import run_task
from predictor import predict_load
from dqn_agent import select_vm

# -------------------------------
# CONFIG
# -------------------------------
DEFAULT_VMS = ["vm1", "vm2", "vm3"]

VM_CAPACITY = 100
SLA_THRESHOLD = 0.50   

TASKS = [
    "tasks/cpu_task.py",
    "tasks/memory_task.py",
    "tasks/network_task.py"
]

# -------------------------------
# SYSTEM COUNTERS
# -------------------------------
total_tasks = 0
successful_tasks = 0
sla_violations = 0


# -------------------------------
# SAVE METRICS FUNCTION
# -------------------------------
def save_live_metrics(metrics, active_vms, avg_load,
                      last_selected_vm=None, last_reward=None):

    data = {}

    if os.path.exists("metrics.json"):
        try:
            with open("metrics.json", "r") as f:
                data = json.load(f)
        except:
            data = {}

    data["metrics"] = metrics
    data["active_vms"] = active_vms
    data["avg_load"] = avg_load
    data["total_tasks"] = total_tasks
    data["successful_tasks"] = successful_tasks
    data["sla_violations"] = sla_violations

    if "decision_log" not in data:
        data["decision_log"] = []

    if last_selected_vm is not None and last_reward is not None:
        data["decision_log"].append({
            "time": time.strftime("%H:%M:%S"),
            "selected_vm": last_selected_vm,
            "reward": round(last_reward, 2),
            "avg_predicted_load": round(avg_load, 2)
        })

    with open("metrics.json", "w") as f:
        json.dump(data, f, indent=4)


print("[INFO] Starting Adaptive Load Balancer Controller...")


# -------------------------------
# INITIALIZE METRICS.JSON
# -------------------------------
if not os.path.exists("metrics.json"):

    print("[INFO] Creating initial metrics.json...")

    default_metrics = {
        vm: {
            "cpu": random.randint(30, 70),      
            "memory": random.randint(30, 60),
            "network": random.randint(100, 300),
            "tasks": 0
        }
        for vm in DEFAULT_VMS
    }

    save_live_metrics(default_metrics, DEFAULT_VMS, avg_load=0)


# -------------------------------
# MAIN LOOP
# -------------------------------
while True:

    try:
        with open("metrics.json", "r") as f:
            data = json.load(f)

        metrics = data.get("metrics", {})
        active_vms = data.get("active_vms", DEFAULT_VMS)

    except Exception as e:
        print("[ERROR] Reading metrics.json failed:", e)
        time.sleep(5)
        continue

    if not active_vms:
        time.sleep(5)
        continue

    # -------------------------------
    # PREDICT LOAD FOR EACH VM
    # -------------------------------
    predictions = {}

    for vm in active_vms:
        if vm in metrics:
            predictions[vm] = predict_load(metrics[vm])
        else:
            predictions[vm] = 0

    # -------------------------------
    # SELECT VM USING DQN
    # -------------------------------
    selected_vm, last_reward = select_vm(
        predictions, metrics, active_vms
    )

    # -------------------------------
    # ASSIGN RANDOM TASK
    # -------------------------------
    task = random.choice(TASKS)

    print(f"\n[TASK] {task} → {selected_vm} "
          f"(Predicted: {predictions[selected_vm]:.2f})")

    run_task(selected_vm, task)

    # -------------------------------
    # UPDATE SYSTEM METRICS
    # -------------------------------
    total_tasks += 1

    vm_cpu = metrics[selected_vm]["cpu"]

    sla_threshold_value = SLA_THRESHOLD * VM_CAPACITY

    if vm_cpu >= sla_threshold_value:
        sla_violations += 1
        print(f"[SLA]  Violation on {selected_vm} (CPU={vm_cpu}%)")
    else:
        successful_tasks += 1
        print(f"[SLA]  Success on {selected_vm}")

    # Update task counter safely
    metrics[selected_vm]["tasks"] = \
        metrics[selected_vm].get("tasks", 0) + 1

    # -------------------------------
    # CALCULATE AVERAGE PREDICTED LOAD
    # -------------------------------
    avg_load = sum(predictions.values()) / len(predictions)

    # -------------------------------
    # SAVE EVERYTHING
    # -------------------------------
    save_live_metrics(
        metrics,
        active_vms,
        avg_load,
        selected_vm,
        last_reward
    )

    # -------------------------------
    # COOL DOWN INTERVAL
    # -------------------------------
    time.sleep(15)