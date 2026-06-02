#cpu_task
import time

while True:
    x = 0
    for i in range(2000000):   
        x += i * i

    time.sleep(1)   
