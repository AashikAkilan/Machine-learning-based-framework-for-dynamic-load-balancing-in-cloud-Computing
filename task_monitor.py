import psutil
import time
import json

old_net = psutil.net_io_counters()

while True:
    # Wait exactly 1 second
    time.sleep(1)

    new_net = psutil.net_io_counters()

    # Calculate total network speed (sent + received)
    bytes_sent = new_net.bytes_sent - old_net.bytes_sent
    bytes_recv = new_net.bytes_recv - old_net.bytes_recv

    net_speed = (bytes_sent + bytes_recv) / 1024  # KB/s

    old_net = new_net

    data = {
        "cpu": psutil.cpu_percent(interval=None),
        "memory": psutil.virtual_memory().percent,
        "network": net_speed
    }

    print(json.dumps(data), flush=True)
