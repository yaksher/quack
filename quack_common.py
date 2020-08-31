import os, sys
import discord
import re
from discord.ext import commands
import io
import asyncio
import time

tech_id = 659440262422069269
ace_id = 463225414534430721

yak_id = 133270838605643776
slav_id = 193701039633989632
admin_ids = [yak_id, slav_id]

ready = """print('Logged in as')
print(bot.user.name)
print(bot.user.id)
print(" ".join(sys.argv))
print('------')"""

def restart_func(user_id):
    if user_id in admin_ids:
        os.execl(sys.executable, sys.executable, *sys.argv)