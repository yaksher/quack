import discord
import re
import requests
from discord.ext import commands
from collections import Counter
import sys
import gpt_2_simple as gpt2

description = ""

bot = commands.Bot(command_prefix='?', description=description)

sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, run_name=sys.argv[1])

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

def log_com(ctx, perms=True):
    print("Command called: \"" + ctx.message.content.split(" ")[0] + "\" in channel: \"" + ctx.channel.name + "\"")
    if not perms:
        print("User did not have permissions.")

@bot.command()
async def xerai(ctx, tokens: int, *args):
    log_com(ctx)
    prefix = " ".join(args)
    message = await ctx.channel.send("Please stand by. This'll take a bit.")
    tokens = min(tokens, 1023)
    global sess
    text = gpt2.generate(sess,
              length=tokens,
              temperature=0.9,
              prefix=prefix,
              return_as_list=True)[0]
    text = text.replace("<::>", ":").replace("<:end message:>", "")
    if (len(text) < 2200):
        await ctx.channel.send(text[:2000])
    else:
        f = open("gpt2_out.txt", "w")
        f.write(text)
        f.close()
        await ctx.channel.send(file=discord.File("gpt2_out.txt"))
    await message.delete()


f = open("maintoken.txt", "r")
token = f.readlines()[0]
bot.run(token)
