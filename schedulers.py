'''import copy

SLA_THRESHOLD = 0.90   # 90% capacity limit


# ==========================================================
# ROUND ROBIN SCHEDULER
# ==========================================================
def round_robin(tasks, vm_template):

    vms = copy.deepcopy(vm_template)
    vm_index = 0

    successful = 0
    sla_violations = 0

    for task in tasks:

        vm = vms[vm_index]
        vm_index = (vm_index + 1) % len(vms)

        if vm["cpu"] + task["cpu"] <= SLA_THRESHOLD * vm["capacity"]:
            vm["cpu"] += task["cpu"]
            successful += 1
        else:
            sla_violations += 1

    return successful, sla_violations


# ==========================================================
# FIRST FIT SCHEDULER
# ==========================================================
def first_fit(tasks, vm_template):

    vms = copy.deepcopy(vm_template)

    successful = 0
    sla_violations = 0

    for task in tasks:

        allocated = False

        for vm in vms:
            if vm["cpu"] + task["cpu"] <= SLA_THRESHOLD * vm["capacity"]:
                vm["cpu"] += task["cpu"]
                successful += 1
                allocated = True
                break

        if not allocated:
            sla_violations += 1

    return successful, sla_violations


# ==========================================================
# RANDOM SCHEDULER
# ==========================================================
def random_allocation(tasks, vm_template):

    import random
    vms = copy.deepcopy(vm_template)

    successful = 0
    sla_violations = 0

    for task in tasks:

        vm = random.choice(vms)

        if vm["cpu"] + task["cpu"] <= SLA_THRESHOLD * vm["capacity"]:
            vm["cpu"] += task["cpu"]
            successful += 1
        else:
            sla_violations += 1

    return successful, sla_violations
'''
import copy
import random

SLA_THRESHOLD = 0.90   # 90% capacity limit
CPU_DECAY = 5          # Simulated CPU release per iteration


# ==========================================================
# ROUND ROBIN SCHEDULER
# ==========================================================
def round_robin(tasks, vm_template):

    vms = copy.deepcopy(vm_template)
    vm_index = 0

    successful = 0
    sla_violations = 0

    for task in tasks:

        vm = vms[vm_index]
        vm_index = (vm_index + 1) % len(vms)

        # SLA Check
        if vm["cpu"] + task["cpu"] <= SLA_THRESHOLD * vm["capacity"]:
            vm["cpu"] += task["cpu"]
            successful += 1
        else:
            sla_violations += 1

        # Simulate CPU release for all VMs
        for v in vms:
            v["cpu"] = max(0, v["cpu"] - CPU_DECAY)

    return successful, sla_violations


# ==========================================================
# FIRST FIT SCHEDULER
# ==========================================================
def first_fit(tasks, vm_template):

    vms = copy.deepcopy(vm_template)

    successful = 0
    sla_violations = 0

    for task in tasks:

        allocated = False

        for vm in vms:
            if vm["cpu"] + task["cpu"] <= SLA_THRESHOLD * vm["capacity"]:
                vm["cpu"] += task["cpu"]
                successful += 1
                allocated = True
                break

        if not allocated:
            sla_violations += 1

        # Simulate CPU release
        for v in vms:
            v["cpu"] = max(0, v["cpu"] - CPU_DECAY)

    return successful, sla_violations


# ==========================================================
# RANDOM SCHEDULER
# ==========================================================
def random_allocation(tasks, vm_template):

    vms = copy.deepcopy(vm_template)

    successful = 0
    sla_violations = 0

    for task in tasks:

        vm = random.choice(vms)

        if vm["cpu"] + task["cpu"] <= SLA_THRESHOLD * vm["capacity"]:
            vm["cpu"] += task["cpu"]
            successful += 1
        else:
            sla_violations += 1

        # Simulate CPU release
        for v in vms:
            v["cpu"] = max(0, v["cpu"] - CPU_DECAY)

    return successful, sla_violations
