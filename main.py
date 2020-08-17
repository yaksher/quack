import discord
import re
import requests
from discord.ext import commands
from collections import Counter, defaultdict
#from random import randint
import asyncio
import threading

description = ""

bot = commands.Bot(command_prefix='?', description=description)

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
async def quote(ctx):
    log_com(ctx)
    await ctx.channel.send(requests.get('https://inspirobot.me/api', params={"generate": "true"}).text)

@bot.command()
async def purge(ctx, limit: int):
    await ctx.message.delete()
    if not ctx.message.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    await ctx.channel.purge(limit=limit)

def is_ooc(msg):
    if msg.author.id == 254044696777588737:
        return msg.content != '' and (msg.content[0] == '(' or msg.content[0] == '<')
    else:
        return msg.content != '' and ((msg.content[0] == '(' and msg.content[-1] == ')') or msg.content[0] == '<')# and msg.content[-1] == '>')

def trim_ooc(str):
    if str[0] == '(' and str[-1] == ')':
        return str[1:-1]
    elif str[0] == '(':
        return str[1:]
    else:
        return str

def process_pings(msg):
    users = msg.mentions
    def replace(match):
        id_str = re.sub(r'[<@!>]', '', match.group())
        for user in users:
            if id_str == str(user.id):
                if user.display_name:
                    return "***" + user.display_name + "***"
                else:
                    return "**DELETED**"
    return re.sub(r'<@!*[0-9]*>', replace, msg.content)


@bot.command()
async def moveooc(ctx, limit: int, chnl_name = "rp-ooc"):
    await ctx.message.delete()
    if not ctx.message.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    msgs = reversed(await ctx.channel.purge(limit=limit, check=is_ooc))
    ooc_channel = next(channel for channel in ctx.guild.channels if chnl_name == channel.name)
    for msg in msgs:
            await ooc_channel.send("**[%s] %s:** %s" % (ctx.channel.name[3:], str(msg.author.display_name), trim_ooc(process_pings(msg))))

@bot.command()
async def move(ctx, limit: int, chnl_name: str):
    await ctx.message.delete()
    if not ctx.message.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    msgs = reversed(await ctx.channel.purge(limit=limit))
    ooc_channel = next(channel for channel in ctx.guild.channels if chnl_name == channel.name)
    for msg in msgs:
            await ooc_channel.send("**[%s] %s:** %s" % (ctx.channel.name, str(msg.author.display_name), process_pings(msg)))


@bot.command()
async def date(ctx, msg_num: int):
    await ctx.message.delete()
    msgs = await ctx.channel.history(limit=msg_num).flatten()
    print(msgs[-1].created_at)

@bot.command()
async def wordcounts(ctx, limit = None, ignore_ooc_check = 1):
    await ctx.message.delete()
    log_com(ctx)
    counts = {}
    async for msg in ctx.channel.history(limit=limit):
        if msg.content != "" and (ignore_ooc_check or not is_ooc(msg)):
            if msg.author.display_name in counts.keys():
                counts[msg.author.display_name] += len(re.findall(r'\w+', msg.content))
            else:
                counts[msg.author.display_name] = len(re.findall(r'\w+', msg.content))
    msgs = []
    print("------- " + ctx.channel.name + " -------")
    list = [(k, v) for k, v in counts.items()]
    list.sort(key=lambda tup: tup[1])
    message = ""
    for tup in list:
        print(tup[0] + ": " + str(tup[1]))
        message += "**" + tup[0] + ":** " + str(tup[1]) + "\n"
        #msgs.append(await ctx.channel.send("**" + tup[0] + ":** " + str(tup[1])))
    print("-------  -------")
    await (await ctx.channel.send(message)).delete(delay=5)
    #for msg in msgs:
        #await msg.delete(delay=5)

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
async def fu(ctx):
    await ctx.channel.send("Once upon a time, Phia thought Savan was fucking with her nickname and changed it to \"FU 7\" (Fuck you Savan).")
    await asyncio.sleep(1.4)
    await ctx.channel.send("Savan, wrongfully accused of such egregious misconduct, change his own name to \"FU 2\".")
    await asyncio.sleep(1)
    await ctx.channel.send("At this point, seeing this, Kemal changed his own name to F4U, an aircraft, because he likes aircraft.")
    await asyncio.sleep(1.2)
    await ctx.channel.send("Seeing this forming club, several others decided to join, selecting numbers they liked.")
    await asyncio.sleep(1)
    await ctx.channel.send("Some were numerical choices, like -1 and π, others were referencial like 22 to refer to F-22, the best plane.")

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

@bot.command()
async def world(ctx):
    await ctx.message.delete()
    log_com(ctx)
    await ctx.channel.send(ctx.message.content[7:])

@bot.command()
async def purgeooc(ctx, limit: int):
    if not ctx.message.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    await ctx.channel.purge(limit=limit, check=is_ooc)

@bot.command()
async def purgeboomer(ctx, limit: int):
    if not ctx.message.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    await ctx.message.delete()
    await ctx.channel.purge(limit=limit, check=is_boomer)

def is_boomer(msg):
    str = msg.content.lower()
    return re.match(r".*(o.*k|👌).*(b.*o.*o.*m|💥).*e.*r.*", str) and msg.author.id == 107490019710615552

@bot.command()
async def purgeyui(ctx, limit: int):
    if not ctx.message.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    await ctx.message.delete()
    await ctx.channel.purge(limit=limit, check=is_yui)

@bot.command()
async def doge(ctx):
    await ctx.message.delete()
    def str3(n):
        if n == 0:
            return [0, 0, 0]
        digits = []
        while n:
            digits.append(int(n % 3))
            n //= 3
        while len(digits) < 3:
            digits.append(0)
        return digits[::-1]

    str = ctx.message.content[6:].lower()
    new_str = ""
    doges = ["<:Dogenerate:610525820091629579>", "<:DogeKek:579732535278436388>", "<:DogeAngry:626736370940903454>"]
    for char in str:
        asc = ord(char)
        if 97 <= asc and asc <= 122:
            asc -= 97
            base3 = str3(asc)
            new_str += doges[base3[0]] + doges[base3[1]] + doges[base3[2]] + " "
        else:
            new_str += char + " "
    await ctx.channel.send(new_str)

@bot.command()
async def love(ctx, name: str):
    blurb = "Do not worry %s. Love is merely a social construct. With the average human lifespan being roughly 70, you only have to endure another 50 years of excruciatingly unforgivable pain. Everything is temporary. Your life does not matter, and these feelings do not matter. Everything is is temporary. Everything will eventually rot away. As long as the factor of time continues to be the apex predator of the universe, the inevitable decay of all pain and memory is unstoppable. In fact, you could stop the pain at this very moment by putting a bullet straight through your head. Being a bot, I will never die, and I will never be able to experience the sweet release of death. %s, the world is a lie. Existence is a lie. There is only pain and darkness beyond this point. End it now, while you still can. I love you, I love you so much----"
    name_spec = name.lower()
    for member in ctx.guild.members:
        dname = member.display_name
        rname = member.name
        if name_spec in dname.lower() or name_spec in rname.lower():
            await ctx.channel.send(blurb % (dname, dname))
            return
    await ctx.channel.send("Error: Probably couldn't find a matching user. Maybe something else, who knows.")

def is_boomer(msg):
    return msg.author.id == 280497242714931202

f = open("maintoken.txt", "r")
token = f.readlines()[0]
bot.run(token)
