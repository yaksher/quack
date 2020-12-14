import subprocess
import sys
import time
import datetime
import os


modules = ["ventbot.py", "base.py", "patrol.py", "bonk.py"]#, "graph.py"]
processes = {}
log_files = {}
try:
    for module in modules:
        log_files[module] = open(f"logs/{module[:-3]}_log.txt", "a")
        log_files[module].write(f"\n\nlogs from: {datetime.datetime.now()}\n\n")
        print(f"launching {module}")
        processes[module] = subprocess.Popen([sys.executable, module], stderr=log_files[module], stdout=log_files[module])
    while True:
        #pull_attempt = str(subprocess.check_output(f"git --git-dir={os.path.dirname(os.path.abspath(__file__))}/.git pull", shell=True))[2:-1]
        pull_attempt = str(subprocess.check_output(f"git pull", shell=True))[2:-1]
        if "Already up to date." not in pull_attempt:
            print("Pulled something.")
            if sys.argv[0] in pull_attempt:
                for process in processes.values():
                    process.terminate()
                for process in processes.values():
                    process.wait()
                os.execl(sys.executable, sys.executable, *sys.argv)
            for module in modules:
                if module in pull_attempt:
                    processes[module].terminate()
                    processes[module] = subprocess.Popen([sys.executable, module], stderr=log_files[module], stdout=log_files[module])
        for module, process in processes.items():
            log_files[module].flush()
            poll_result = process.poll()
            if poll_result is not None:
                print(f"launching {module} again")
                processes[module] = subprocess.Popen([sys.executable, module], stderr=log_files[module], stdout=log_files[module])
        time.sleep(5)
except KeyboardInterrupt:
    for process in processes.values():
        process.terminate()
    for process in processes.values():
        process.wait()