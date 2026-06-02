from simulation import run_simulation


# ----------------------------------------------------------
# METRIC FUNCTIONS
# ----------------------------------------------------------
def allocation_accuracy(total, success):
    return (success / total) * 100


def sla_compliance(total, violations):
    return (1 - violations / total) * 100


# ----------------------------------------------------------
# RUN COMPARISON
# ----------------------------------------------------------
if __name__ == "__main__":

    results, total_tasks = run_simulation(1000)

    print("\n============= ALGORITHM COMPARISON =============\n")

    print(f"Total Tasks: {total_tasks}\n")

    print("{:<15} {:<20} {:<20}".format(
        "Algorithm",
        "Allocation Accuracy (%)",
        "SLA Compliance (%)"
    ))

    print("-" * 60)

    for algo, (success, violations) in results.items():

        alloc_acc = allocation_accuracy(total_tasks, success)
        sla_rate = sla_compliance(total_tasks, violations)

        print("{:<15} {:<20.2f} {:<20.2f}".format(
            algo,
            alloc_acc,
            sla_rate
        ))

    print("\n=================================================\n")
