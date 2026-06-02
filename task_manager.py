import paramiko

VM_IPS = {
    "vm1": "192.168.56.101",
    "vm2": "192.168.56.102",
    "vm3": "192.168.56.103"
}

USERNAME = "kali"
PASSWORD = "kali"

def run_task(vm, task_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(VM_IPS[vm], username=USERNAME, password=PASSWORD)

    cmd = f"nohup python3 {task_file} > /dev/null 2>&1 &"
    ssh.exec_command(cmd)

    print(f"[TASK] Started {task_file} on {vm}")

