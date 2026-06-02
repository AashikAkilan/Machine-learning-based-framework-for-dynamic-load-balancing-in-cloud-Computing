import psutil
import time
import json

old_net = psutil.net_io_counters().bytes_sent

while True:
    new_net = psutil.net_io_counters().bytes_sent
    net_speed = (new_net - old_net) / 1024   # KB/s
    old_net = new_net

    data = {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "network": net_speed
    }

    print(json.dumps(data), flush=True)
    time.sleep(2)


