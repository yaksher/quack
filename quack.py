import subprocess
import sys
import time

out_file = open("log_out.txt", "a")
err_file = open("log_err.txt", "a")

sys.stdout = out_file
sys.stderr = err_file


modules = ["ventbot.py", "base.py", "patrol.py", "graph.py"]
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