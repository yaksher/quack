import discord
from discord.ext import commands
import asyncio
import json
import time

description = ""

bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

f = open("rick.json")
lyrics = json.load(f)["values"]
f.close()

COOLDOWN = 0

last_call = time.time() - COOLDOWN

ready = True
kill = False

@bot.command()
async def hell(ctx):
    print(ctx.message.author, ctx.channel)
    if ctx.guild.id == 659440262422069269:
        await ctx.channel.send("Tom asked me to turn this off.")
        return
    global COOLDOWN
    global last_call
    global ready
    if time.time() - last_call < COOLDOWN:
        return
    if not ready:
        await ctx.channel.send("Hell is singular. (And busy)")
        return
    last_call = time.time()
    ready = False
    global kill
    start = time.time() * 1000
    for i in range(len(lyrics)):
        elapsed = time.time() * 1000 - start
        await asyncio.sleep((lyrics[i]["time"] - elapsed)/1000)
        if kill:
            ready = True
            kill = False
            return
        await ctx.channel.send(lyrics[i]["lyric"])
    ready = True

@bot.command()
async def end_this_hell(ctx):
    global kill
    global ready
    if not ready:
        kill = True

@bot.command()
async def rickroll(ctx):
    print(ctx.message.author, ctx.channel)
    if ctx.guild.id == 659440262422069269:
        await ctx.channel.send("Tom asked me to turn this off.")
        return
    global COOLDOWN
    global last_call
    global ready
    if time.time() - last_call < COOLDOWN or not ready:
        return
    last_call = time.time()
    ready = False
    global kill
    start = time.time() * 1000
    for i in range(len(lyrics)):
        elapsed = time.time() * 1000 - start
        await asyncio.sleep((lyrics[i]["time"] - elapsed)/1000)
        if kill:
            ready = True
            kill = False
            return
        await ctx.channel.send(lyrics[i]["lyric"])
    ready = True

f = open("maintoken.txt", "r")
token = f.readlines()[0]
f.close()
bot.run(token)
