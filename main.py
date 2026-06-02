import subprocess
import time
import sys
import signal

print("Starting VM Task Monitors...")
vm1 = subprocess.Popen([sys.executable, "task_monitor.py"])
vm2 = subprocess.Popen([sys.executable, "task_monitor.py"])
vm3 = subprocess.Popen([sys.executable, "task_monitor.py"])

time.sleep(2)

print("Starting Monitor Service...")
monitor = subprocess.Popen([sys.executable, "monitor_service.py"])

time.sleep(2)

print("Starting Controller...")
controller = subprocess.Popen([sys.executable, "controller.py"])

time.sleep(2)

print("Starting Dashboard...")
dashboard = subprocess.Popen(["streamlit", "run", "dashboard.py"])

processes = [vm1, vm2, monitor, controller, dashboard]


# Proper shutdown handler
def signal_handler(sig, frame):
    print("\nStopping all services safely...")

    for p in processes:
        try:
            p.terminate()   # Graceful stop
        except:
            pass

    time.sleep(2)

    for p in processes:
        try:
            if p.poll() is None:
                p.kill()    # Force stop if still running
        except:
            pass

    print("All services stopped.")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

print("All services started! ")

# Keep main alive
while True:
    time.sleep(1)
