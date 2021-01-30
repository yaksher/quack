import subprocess
import sys
import time
import datetime
import os

# this comment is still a random change for test commit

module_files = ["ventbot.py", "base.py", "patrol.py", "bonk.py"]#, "graph.py"]
class Module:
    def __init__(self, name, filename):
        self.name = name
        try:
            self.log = open(f"logs/{self.name}_log.txt", "a")
        except FileNotFoundError:
            self.log = open(f"logs/{self.name}_log.txt", "w")
        self.log.write(f"\n\nlogs from: {datetime.datetime.now()}\n\n")
        self.file = filename
        self.process = None
        self.launch_time = None
        print(f"Initialized {self.name}")

    def launch(self):
        self.process = subprocess.Popen([sys.executable, self.file], stderr=self.log, stdout=self.log)
        self.launch_time = time.time()
        print(f"Launched {self.name}")

    def restart(self):
        self.kill()
        self.launch()
        print(f"Restarting {self.name}")

    def cond_restart(self):
        last_modified = os.path.getmtime(self.file)
        self.log.flush()
        if last_modified > self.launch_time or self.process.poll() is not None:
            self.restart()

    def kill(self):
        self.process.terminate()
        return self.process

class ModuleManager:
    def __init__(self, files, loop_time):
        self.modules = [Module(f[:-3], f) for f in files]
        self.loop_time = loop_time
        self.init = time.time()

    def __iter__(self):
        return self.modules.__iter__()
    
    def run(self):
        try:
            for module in self:
                module.launch()
            while True:
                self.cond_restart()

                for module in self:
                    module.cond_restart()
                
                time.sleep(self.loop_time)
        except KeyboardInterrupt:
            self.kill_all()

    def cond_restart(self):
        if os.path.getmtime(sys.argv[0]) > self.init:
            self.kill_all()
            os.execl(sys.executable, sys.executable, *sys.argv)

    def kill_all(self):
        for p in [module.kill() for module in self]:
            p.wait()

manager = ModuleManager(module_files, 5)

manager.run()