import subprocess
import sys
import time
import os

log_file = open("quack_log.txt", "a")
log_file.write("\n\n\n")
sys.stdout = log_file
sys.stderr = log_file


modules = ["ventbot.py", "base.py", "patrol.py"]#, "graph.py"]
processes = {}
log_files = {}
try:
    for module in modules:
        log_files[module] = open(f"{module[:-3]}_log.txt", "a")
        log_files[module].write("\n\n\n")
        processes[module] = subprocess.Popen([sys.executable, module], stderr=log_files[module], stdout=log_files[module])
    while True:
        pull_attempt = str(subprocess.check_output(f"git --git-dir={os.path.dirname(os.path.abspath(__file__))}/.git pull", shell=True))
        if "Already up to date." not in pull_attempt:
            if sys.executable in pull_attempt:
                os.execl(sys.executable, sys.executable, *sys.argv)
            for module in modules:
                if module in pull_attempt:
                    processes[module].terminate()
                    processes[module].wait()
                    processes[module] = subprocess.Popen([sys.executable, module], stderr=log_files[module], stdout=log_files[module])
        for module, process in processes.items():
            poll_result = process.poll()
            if poll_result is not None:
                processes[module] = subprocess.Popen([sys.executable, module], stderr=log_files[module], stdout=log_files[module])
        time.sleep(5)
except KeyboardInterrupt:
    for process in processes.values():
        process.terminate()
    for process in processes.values():
        process.wait()