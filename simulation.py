import numpy as np
from schedulers import round_robin, first_fit, random_allocation


# ----------------------------------------------------------
# GENERATE TASKS
# ----------------------------------------------------------
def generate_tasks(num_tasks=200):

    tasks = []

    for _ in range(num_tasks):
        task = {
            "cpu": np.random.randint(10, 60)
        }
        tasks.append(task)

    return tasks


# ----------------------------------------------------------
# CREATE VMs
# ----------------------------------------------------------
def create_vms(num_vms=5, capacity=100):

    vms = []

    for i in range(num_vms):
        vms.append({
            "id": i,
            "cpu": 0,
            "capacity": capacity
        })

    return vms


# ----------------------------------------------------------
# RUN ALL SCHEDULERS
# ----------------------------------------------------------
def run_simulation(num_tasks=200):

    tasks = generate_tasks(num_tasks)

    vm_template = create_vms()

    results = {}

    # Round Robin
    rr_success, rr_sla = round_robin(tasks, vm_template)
    results["Round Robin"] = (rr_success, rr_sla)

    # First Fit
    ff_success, ff_sla = first_fit(tasks, vm_template)
    results["First Fit"] = (ff_success, ff_sla)

    # Random
    rnd_success, rnd_sla = random_allocation(tasks, vm_template)
    results["Random"] = (rnd_success, rnd_sla)

    return results, num_tasks
