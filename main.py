import subprocess
import sys

modules = ["fauxclient.py", "base.py", "patrol.py", "graph.py"]
processes = []
try:
    for module in modules:
        processes.append(subprocess.Popen([sys.executable, module]))
    for process in processes:
        process.wait()
except KeyboardInterrupt:
    for process in processes:
        process.terminate()
    for process in processes:
        process.wait()