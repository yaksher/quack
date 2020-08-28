import subprocess
import sys
import time
import os

out_file = open("log_out.txt", "a")
err_file = open("log_err.txt", "a")
out_file.write("\n\n\n")
err_file.write("\n\n\n")
sys.stdout = out_file
sys.stderr = err_file


modules = ["ventbot.py", "base.py", "patrol.py"]#, "graph.py"]
processes = {}
try:
    for module in modules:
        processes[module] = subprocess.Popen([sys.executable, module])
    while True:
        pull_attempt = subprocess.check_output(f"git --git-dir={os.path.dirname(os.path.abspath(__file__))} pull", shell=True)
        if "Already up to date." not in pull_attempt:
            if sys.executable in pull_attempt:
                os.execl(sys.executable, sys.executable, *sys.argv)
            for module in modules:
                if module in pull_attempt:
                    processes[module].terminate()
                    processes[module].wait()
                    processes[module] = subprocess.Popen([sys.executable, module])
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