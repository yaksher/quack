import discord
import re
import requests
from discord.ext import commands
from collections import Counter, defaultdict
#from random import randint
import asyncio

description = ""

bot = commands.Bot(command_prefix='?', description=description)

@bot.command()
async def date(ctx, msg_num: int):
    await ctx.message.delete()
    msgs = await ctx.channel.history(limit=msg_num).flatten()
    print(msgs[-1].created_at)

@bot.command()
async def gettext(ctx, include_ooc = 0):
    await ctx.message.delete()
    if not ctx.message.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    f = open(ctx.channel.name + ".txt", "w+")
    async for msg in ctx.channel.history(limit=None, oldest_first=True):
        if msg.content != "" and (include_ooc or not is_ooc(msg)):
            f.write(msg.content + "\n\n")

@bot.command()
async def nettext(ctx, ooc_channel=0, ooc=0):
    await ctx.message.delete()
    if not ctx.message.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    f = open(ctx.channel.name + "-rip.txt", "w+")
    if not ooc_channel:
        if not ooc:
            async for msg in ctx.channel.history(limit=None, oldest_first=True):
                if msg.content != "" and not is_ooc(msg):
                    f.write(msg.content + "{r}")
        else:
            async for msg in ctx.channel.history(limit=None, oldest_first=True):
                if msg.content != "" and is_ooc(msg):
                    f.write(trim_ooc(process_pings(msg)) + "{r}")
    else:
        async for msg in ctx.channel.history(limit=None, oldest_first=True):
            if msg.author == bot.user:
                f.write(re.sub(r'(^\*\*.*:\*\* )|(^.*#[0-9]{4} @[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}: )','',msg.content) + "{r}")

@bot.command()
async def getchannels(ctx):
    print(ctx.guild.channels)

@bot.command()
async def getmessages(ctx):
    try:
        await ctx.message.delete()
    except discord.errors.Forbidden:
        pass
    log_com(ctx)
    f = open("all_messages_%s.txt" % ctx.guild.name, "w")
    name_seperator_token = " <::> "
    msg_end_token = "<:end message:>\n"
    channel_contents = defaultdict(lambda: "")
    async def download(channel):
        print(f"started: {channel.name}")
        try:
            async for msg in channel.history(limit=None, oldest_first=True):
                if len(msg.content) != 0:
                    channel_contents[channel.name] += f"{msg.author.name}{name_seperator_token}{msg.content}{msg_end_token}"
        except discord.errors.Forbidden:
                pass
        tasks_rem[0] -= 1
        print(f"finished: {channel.name} | remaining {tasks_rem[0]}")
    tasks = []
    tasks_rem = [0]
    chnl_blacklist = [474311707339128863, 659560407807033364, 662912082559369236]
    for channel in ctx.guild.channels:
        if type(channel) is discord.TextChannel and not channel.id in chnl_blacklist:
            tasks.append(asyncio.create_task(download(channel)))
    tasks_rem[0] = len(tasks)
    for task in tasks:
        await task
    for key, value in channel_contents.items():
        f.write(value)
            

from datetime import datetime
@bot.command()
async def servercounts(ctx):
    try:
        await ctx.message.delete()
    except discord.errors.Forbidden:
        pass
    log_com(ctx)
    f = open(f"{ctx.guild.name}_{datetime.now()}.txt", "w+")
    counts = defaultdict(lambda: 0)
    channel_counts = defaultdict(lambda: 0)
    message_counts = defaultdict(lambda: 0)
    async def download(channel):
        print(f"started: {channel.name}")
        try:
            async for msg in channel.history(limit=None):
                msg_words = len(re.findall(r'\w+', msg.content))
                channel_counts[channel.name] += msg_words
                counts[str(msg.author)] += msg_words
                message_counts[str(msg.author)] += 1
        except discord.errors.Forbidden:
                pass
        tasks_rem[0] -= 1
        print(f"finished: {channel.name} | remaining {tasks_rem[0]}")
    tasks = []
    tasks_rem = [0]
    for channel in ctx.guild.channels:
        if type(channel) is discord.TextChannel:
            tasks.append(asyncio.create_task(download(channel)))
    tasks_rem[0] = len(tasks)
    for task in tasks:
        await task
    print("-------  -------")
    p_list = [(k, v, v / message_counts[k]) for k, v in counts.items()]
    p_list.sort(key=lambda tup: tup[2])
    c_list = [(k, v) for k, v in channel_counts.items()]
    c_list.sort(key=lambda tup: tup[1])
    for tup in reversed(p_list):
        f.write(f"{tup[0]}: {tup[1]} : {str(tup[2])[:4]} \n")
        print(f"{tup[0]}: {tup[1]} : {tup[2]}")
    f.write("-------  -------\n")
    print("-------  -------")
    for tup in reversed(c_list):
        f.write(tup[0] + ": " + str(tup[1]) + "\n")
        print(tup[0] + ": " + str(tup[1]))
    print("-------  -------")

@bot.command()
async def servercounts2(ctx):
    await ctx.message.delete()
    log_com(ctx)
    f = open("wordcounts.txt", "w+")
    counts = {}
    channel_counts = {}
    for channel in ctx.guild.channels:
        if type(channel) is discord.TextChannel:
            channel_counts[channel.name] = Counter([])
            print(channel.name)
            async for msg in channel.history(limit=None):
                msg_words = Counter([s.lower() for s in re.findall(r'\w+', msg.content)])
                channel_counts[channel.name] += msg_words
                if msg.author.display_name in counts.keys():
                    counts[msg.author.display_name] += msg_words
                else:
                    counts[msg.author.display_name] = msg_words
    for key, count in counts.items():
        print(key, count)
        f.write(key + ": " + str(count) + "\n")
    """print("-------  -------")
    list = [(k, v) for k, v in counts.items()]
    list.sort(key=lambda tup: tup[1])
    c_list = [(k, v) for k, v in channel_counts.items()]
    c_list.sort(key=lambda tup: tup[1])
    for tup in reversed(list):
        f.write(tup[0] + ": " + str(tup[1]) + "\n")
        print(tup[0] + ": " + str(tup[1]))
    f.write("-------  -------\n")
    print("-------  -------")
    for tup in reversed(c_list):
        f.write(tup[0] + ": " + str(tup[1]) + "\n")
        print(tup[0] + ": " + str(tup[1]))
    print("-------  -------")"""


f = open("maintoken.txt", "r")
token = f.readlines()[0]
bot.run(token)