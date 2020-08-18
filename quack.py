import subprocess
import sys
import time

modules = ["fauxclient.py", "base.py", "patrol.py", "graph.py"]
processes = {}
try:
    for module in modules:
        processes[module] = subprocess.Popen([sys.executable, module])
    while True:
        for module, process in processes.items():
            poll_result = process.poll()
            if poll_result is not None:
                processes[module] = subprocess.Popen([sys.executable, module])
        time.sleep(5)
except KeyboardInterrupt:
    for process in processes.values():
        process.terminate()
    for process in processes.values():
        process.wait()