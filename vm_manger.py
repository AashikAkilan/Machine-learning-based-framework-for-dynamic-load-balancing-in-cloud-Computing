# task_manager.py
import paramiko

VM_IPS = {
    "vm1": "192.168.56.102",
    "vm2": "192.168.56.101",
    "vm3": "192.168.56.103"
}

USERNAME = "kali"
PASSWORD = "kali"

def run_task(vm, task_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(VM_IPS[vm], username=USERNAME, password=PASSWORD, timeout=10)
        cmd = f"python3 {task_file}"
        ssh.exec_command(cmd)
        print(f"Task started on {vm}: {task_file}")
    except Exception as e:
        print(f"Failed to run task on {vm}: {e}")
