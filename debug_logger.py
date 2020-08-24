from quack_common import *

description = ""

bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    exec(ready)

@bot.event
async def on_message(message):
    if message.guild or message.author.id == yak_id:
        print(message.author, message.content)

f = open("maintoken.txt", "r")
token = f.readlines()[0]
bot.run(token)
