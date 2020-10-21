from quack_common import *
import traceback
import readline
import os
histfile = os.path.join(os.path.expanduser("~"), ".quack_pyhist")
try:
    readline.read_history_file(histfile)
    readline.set_history_length(1000)
except IOError:
    pass
import atexit
atexit.register(readline.write_history_file, histfile)
readline.parse_and_bind('set editing-mode vi')
readline.parse_and_bind('tab: tab-insert')
bot = commands.Bot(command_prefix='?', description="")

@bot.event
async def on_ready():
    def get_in(indent=False):
        line = input("... " if indent else ">>> ")
        return line + "\n" + get_in(True) if line.endswith(":") else line
    def wait(func):
        tasks.append(asyncio.create_task(func))
    try:
        while True:
            code = get_in()
            tasks = []
            try:
                if "\n" not in code and not (code.startswith("print(") and code.endswith(")")):
                    try:
                        exec(f"__TEMPORARY__ = ({code})\nprint(__TEMPORARY__ if __TEMPORARY__ is not None else \"\", end=\"\\n\" if __TEMPORARY__ is not None else \"\")")
                        continue
                    except SyntaxError:
                        pass
                exec(code)
                for task in tasks:
                    await task
            except:
                traceback.print_exc()
    except EOFError:
        exit(0)

bot.run(token)