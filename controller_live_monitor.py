# controller_live_monitor.py
import paramiko
import json
import threading

VM_CONFIG = {
    "vm1": "192.168.56.102",
    "vm2": "192.168.56.101",
    "vm3": "192.168.56.103",
}

USERNAME = "kali"
PASSWORD = "kali"

def monitor_vm(name, ip):
    print(f"[+] Connecting to {name} ({ip})")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=USERNAME, password=PASSWORD, timeout=10)
        cmd = "python3 /home/kali/task_monitor.py"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        for line in stdout:
            try:
                data = json.loads(line.strip())
                print(f"{name} → CPU:{data['cpu']} MEM:{data['memory']} NET:{data['network']}")
            except Exception as e:
                pass
    except Exception as e:
        print(f"Failed to connect {name}: {e}")

threads = []

for vm, ip in VM_CONFIG.items():
    t = threading.Thread(target=monitor_vm, args=(vm, ip))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
