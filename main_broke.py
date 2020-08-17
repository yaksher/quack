import discord
import re
from random import randint
from discord.ext import commands
from collections import Counter, defaultdict
import time
import asyncio
import os
import sys
import matplotlib.pyplot as plt
from sympy import *
import numpy as np
import io

description = ""

bot = commands.Bot(command_prefix='?', description=description)

TIMEOUT = 30 * 60

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    while True:
        for channel in subbed:
            if time.time() - session_time[channel.id] > TIMEOUT:
                await channel.send("Session timed out. You will get a new ID for your next message.")
                end_session(channel)
        await asyncio.sleep(TIMEOUT / 3)

@bot.event
async def on_message(msg):
    if msg.author.id == yak_id and msg.content == "?restart":
        restart()
    tasks = []
    tasks.append(asyncio.create_task(fauxclient_msg(msg)))
    tasks.append(asyncio.create_task(patrol_msg(msg)))
    tasks.append(asyncio.create_task(bot.process_commands(msg)))
    for task in tasks:
        await task

change_TSS = True
async def patrol_msg(message):
    global change_TSS
    if message.guild:
        print(message.author, message.content)
    ace_id = 463225414534430721
    if message.guild and message.guild.id == ace_id:
        if is_boomer(message):
            print("Deleted \"ok boomer\" in channel", message.channel)
            await message.delete()
        if is_ooc(message):
            print("Moved OOC message from channel", message.channel)
            ooc_channel = next(channel for channel in message.guild.channels if "rp-ooc" == channel.name)
            await ooc_channel.send("**[%s] %s:** %s" % (message.channel.name[3:], str(message.author.display_name), trim_ooc(process_pings(message))))
            await message.delete(delay=10)
        TSS_ID = 207642057198534656
        if message.author.id == TSS_ID:
            if change_TSS:
                change_TSS = False
                get_nick = getNick()
                await message.author.edit(nick=get_nick[0])
        else:
            change_TSS == True
        for user in message.mentions:
            if user.id == TSS_ID:
                get_nick = getNick()
                await user.edit(nick=get_nick[0])
        if tssName(message.content):
            for m in message.guild.members:
                if m.id == TSS_ID:
                    await m.edit(nick=tssName(message.content))
        if is_hal_summon(message.content):
            ping = await message.channel.send("<@!381597229644775425>")
            await ping.delete()

    if message.content == "&quote":
        await message.channel.send(requests.get('https://inspirobot.me/api', params={"generate": "true"}).text)
    Yak_ID = 133270838605643776
    if message.author.id == Yak_ID:
        role = message.author.roles[-2]
        if message.guild.id == ace_id or role.id == 710307102115102732:
            await role.edit(colour=random_colour())
    for user in message.mentions:
        if user.id == Yak_ID:
            role = user.roles[-2]
            if message.guild.id == ace_id or role.id == 710307102115102732:
                await role.edit(colour=random_colour())
    content_lower = message.content.lower()
    if re.match(r"(.*yakov.*)|(.*yasha.*)", content_lower):
        for m in message.guild.members:
            if m.id == Yak_ID:
                role = m.roles[-2]
                if message.guild.id == ace_id or role.id == 710307102115102732:
                    await role.edit(colour=random_colour())

def random_colour():
    return discord.Colour.from_rgb(randint(0,255),randint(0,255),randint(0,255))

def colour_cycle(t):
    r = int(m.sin((t + 2/3 - 0.1) * 2 * m.pi) * 127) + 128
    g = int(m.sin((t - 0.1) * 2 * m.pi) * 127) + 128
    b = int(m.sin((t + 1/3 - 0.1) * 2 * m.pi) * 127) + 128
    return discord.Colour.from_rgb(r,g,b)

"""@bot.event
async def on_typing(channel, user, when):
    Andy_ID = 269639316408500224
    Yoos_ID = 211743140992909313
    if user.id == Yoos_ID:
        role = user.roles[-1]
        count = 0
        time = 5
        interval = 0.1
        upper = time / interval
        while (count < upper):
            count += 1
            await role.edit(colour=colour_cycle(count / upper))
            await asyncio.sleep(interval)"""

def is_hal_summon(content):
    str = content.lower()
    return re.match(r".*(ps){4,20}.*", str)

def is_boomer(msg):
    str = msg.content.lower()
    #return re.match(r".*(o.*k|👌).*(b.*o.*o.*m|💥).*e.*r.*", str) and msg.author.id == 107490019710615552
    # (o|о|ο) is (latin|russian|greek)
    return re.match(r".*((b|z) *.{0,3}(o|о|ο|🇴) *.{0,3}(o|о|ο|🇴) *.{0,3}(m|м) *.{0,3}|💥) *.{0,3}e *.{0,3}r.*", str) and msg.author.id == 212#107490019710615552

def is_ooc(msg):
    if msg.channel.name[:3] != "rp-" or msg.channel.name == "rp-ooc":
        return False
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

def tssName(str):
    def replace(match):
        return " " + match.group()
    str2 = re.sub(r'[A-Z]', replace, str)
    pre_tokens = list(re.findall(r'\w+', str2))
    tokens = []
    for t in pre_tokens:
        if len(t) > 1:
            tokens.append(t.lower())
    firsts = []
    for t in tokens:
        firsts.append(t[0].lower())
    letter_string = "".join(firsts)
    m = re.search(r'tss',letter_string)
    if m:
        i = m.start()
        name = "".join([t.capitalize() for t in tokens[i:i+3]])
        if len(name) > 3:
            return name


def getNick():
    f = open("tss_nicks.txt", "r")
    nicks = f.readlines()
    f.close()
    if len(nicks) <= 1:
        print("no nicks")
        return (generateNicks(1)[0][:-1], True)
    return (choice(nicks), False)

def writeNicks(n):
    f = open("tss_nicks.txt", "w")
    f.writelines(generateNicks(n))
    f.close()

def generateNicks(n):
    nick = ""
    w1parems = (("sp", "s????*"), ("max", "1000"), ("md", "p"))
    w1opts = requests.get('https://api.datamuse.com/words', params=w1parems).json()
    for w in w1opts:
        if not "tags" in w or not "n" in w["tags"]:
            w1opts.remove(w)
    nicks = []
    while True:
        try:
            w1 = choice(w1opts)["word"].capitalize()
            w2parems = (("sp", "s??*"), ("max", "200"), ("rel_jjb", w1))
            w2opts = requests.get('https://api.datamuse.com/words', params=w2parems).json()
            w2 = choice(w2opts)["word"].capitalize()
            w3parems = (("sp", "t??*"), ("max", "200"), ("rel_jjb", w1))
            w3opts = requests.get('https://api.datamuse.com/words', params=w3parems).json()
            w3 = choice(w3opts)["word"].capitalize()
            nick = w3 + w2 + w1 + "\n"
            nicks.append(nick)
            if len(nicks) >= n:
                break
        except:
            do_nothing_expression = 0
    return nicks

sel_guild = None
sel_channel = None
dm_channel = None

subbed = []
session_time = defaultdict(lambda: time.time())
forward = defaultdict(lambda: True)
small_ids = defaultdict(lambda: randint(0, 999))
message_duplicates = defaultdict(lambda: [])

yak_id = 133270838605643776
slav_id = 193701039633989632
tech_id = 659440262422069269
vent_id = 659559008159531039
admin_ids = [yak_id, slav_id]
admin_ids_bak = admin_ids[:]

async def fauxclient_msg(msg):
    send_id = msg.author.id
    if msg.guild is None and not send_id in admin_ids and send_id != bot.user.id and bot.get_guild(tech_id).get_member(send_id) is not None:
        if not msg.channel in subbed:
            subbed.append(msg.channel)
            await msg.channel.send(f"To stop getting messages from venting and support, type `.silent`. To end your session, type `.end`. Session expires after 30 minutes of inactivity. Your ID is {small_ids[msg.channel.id]}.")
        if msg.content.lower() in [".end", ".unsub"]:
            end_session(msg.channel)
            await msg.channel.send("Session ended.")
            return
        elif msg.content.lower() in [".stop", ".silent"]:
            forward[msg.channel.id] = False
            await msg.channel.send("No longer forwarding messages from venting. Type `.forward` to get messages again.")
            return
        elif msg.content.lower() in [".forward", ".start"]:
            forward[msg.channel.id] = True
            await msg.channel.send("Now forwarding messages. Type `.stop` to stop.")
            return
        file_ = await msg.attachments[0].to_file() if len(msg.attachments) == 1 else None
        files = [await attachment.to_file() for attachment in msg.attachments] if len(msg.attachments) > 1 else None
        session_time[msg.channel.id] = time.time()
        sent_msg = await bot.get_channel(vent_id).send(f"**{small_ids[msg.channel.id]}**: {process_msg(msg)}", file = file_, files = files)
        message_duplicates[sent_msg.id].append(msg)
        message_duplicates[msg.id].append(sent_msg)
        return
    if msg.channel.id == vent_id:
        file_ = await msg.attachments[0].to_file() if len(msg.attachments) == 1 else None
        files = [await attachment.to_file() for attachment in msg.attachments] if len(msg.attachments) > 1 else None
        for channel in subbed:
            if forward[channel.id] and not msg.content.startswith(f"**{small_ids[channel.id]}**"):
                sent_msg = await channel.send(f"**{msg.author.display_name}** ({msg.author}): {msg.content}", file = file_, files = files)
                message_duplicates[msg.id].append(sent_msg)
                message_duplicates[sent_msg.id].append(msg)
    global sel_guild
    global sel_channel
    global dm_channel
    if send_id in admin_ids:
        if msg.guild == None:
            dm_channel = msg.channel
            if msg.content == "vent":
                admin_ids.remove(send_id)
                subbed.append(msg.channel)
                await msg.channel.send(f"To stop getting messages from venting and support, type `.silent`. To end your session, type `.end`. Session expires after 30 minutes of inactivity. Your ID is {small_ids[msg.channel.id]}.")
                return
            if msg.content.startswith("cd"):
                cmd = msg.content[3:].split("/")
                if cmd[0] == "..":
                    sel_guild = None
                    sel_channel = None
                elif len(cmd) == 1:
                    if sel_guild:
                        try:
                            sel_channel = bot.get_channel(int(cmd[0]))
                        except ValueError:
                            sel_channel = next(channel for channel in sel_guild.channels if channel.name.lower().startswith(cmd[0].lower()))
                    else:
                        sel_channel = None
                        try:
                            sel_guild = bot.get_guild(int(cmd[0]))
                        except ValueError:
                            sel_guild = next(guild for guild in bot.guilds if guild.name.lower().startswith(cmd[0].lower()))
                elif len(cmd) > 1:
                    try:
                        sel_guild = bot.get_guild(int(cmd[0]))
                    except ValueError:
                        sel_guild = next(guild for guild in bot.guilds if guild.name.lower().startswith(cmd[0].lower()))
                    try:
                        sel_channel = bot.get_channel(int(cmd[1]))
                    except ValueError:
                        sel_channel = next(channel for channel in sel_guild.channels if channel.name.lower().startswith(cmd[1].lower()))
                await msg.channel.send(f"Now in channel {sel_channel} in server {sel_guild}")
            elif msg.content.startswith("ls"):
                await msg.channel.send(f"Now in channel {sel_channel} in server {sel_guild}")
                if msg.content[3:] == ".." or not sel_guild:
                    await msg.channel.send(f"{[guild.name for guild in bot.guilds if send_id == yak_id or guild.id != 692554651941339196]}")
                else:
                    await msg.channel.send(f"{[channel.name for channel in sel_guild.channels if channel.type == discord.ChannelType.text]}")
            elif sel_channel is not None:
                file_ = await msg.attachments[0].to_file() if len(msg.attachments) == 1 else None
                files = [await attachment.to_file() for attachment in msg.attachments] if len(msg.attachments) > 1 else None
                sent_msg = await sel_channel.send(process_msg(msg), file = file_, files = files)
                message_duplicates[sent_msg.id].append(msg)
                message_duplicates[msg.id].append(sent_msg)
        elif msg.content == "?gohere":
            sel_guild = msg.guild
            sel_channel = msg.channel
    elif send_id != bot.user.id and sel_channel and msg.channel.id == sel_channel.id:
        file_ = await msg.attachments[0].to_file() if len(msg.attachments) == 1 else None
        files = [await attachment.to_file() for attachment in msg.attachments] if len(msg.attachments) > 1 else None
        sent_msg = await dm_channel.send(f"**{msg.author.display_name}**: {msg.content}", file = file_, files = files)
        message_duplicates[sent_msg.id].append(msg)
        message_duplicates[msg.id].append(sent_msg)

def end_session(channel):
    if channel.recipient.id in admin_ids_bak:
        admin_ids.append(channel.recipient.id)
    session_time.pop(channel.id, None)
    small_ids.pop(channel.id, None)
    forward.pop(channel.id, None)
    subbed.remove(channel)

def process_msg(msg):
    def replace_emoji(match):
        match_str = match.group()
        name = re.sub(r':', '', match_str)
        for emote in bot.get_guild(659440262422069269).emojis:
            if name == emote.name:
                return f"<:{emote.name}:{emote.id}>"
        return match_str
    emojid_str = re.sub(r'<{0,1}:\w+:[0-9]*>{0,1}', replace_emoji, msg.content)
    def replace_ping(match):
        match_str = match.group()
        try:
            return bot.get_guild(tech_id).get_member_named(match_str[1:]).mention
        except:
            return match_str
    return re.sub(r'(@[\w ]+#[0-9]{4})|(@\w+)', replace_ping, emojid_str)

@bot.event
async def on_reaction_add(reaction, user):
    if user.id != bot.user.id:
        for msg in message_duplicates[reaction.message.id]:
            await msg.add_reaction(reaction.emoji)

@bot.event
async def on_message_delete(message):
    for msg in message_duplicates[message.id]:
        await msg.delete()
    message_duplicates.pop(message.id)

@bot.event
async def on_message_edit(before, after):
    #if before.author.id == bot.user.id:
    #    return
    for msg in message_duplicates[before.id]:
        try:
            if after.guild is None:
                await msg.edit(content=f"**{small_ids[after.channel.id]}**: {process_msg(after)}") 
            else:
                await msg.edit(content=f"**{after.author.display_name}** ({after.author}): {after.content}")
            for dup in message_duplicates[msg.id]:
                message_duplicates[dup.id].remove(msg)
                message_duplicates[dup.id].append(await msg.channel.fetch_message(msg.id))
        except discord.errors.Forbidden:
            pass


def log_com(ctx, perms=True):
    print("Command called: \"" + ctx.message.content.split(" ")[0] + "\" in channel: \"" + ctx.channel.name + "\"")
    if not perms:
        print("User did not have permissions.")

def restart():
    os.system("git pull")
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.command()
async def ping(ctx):
    await ctx.channel.send("pong pong")

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

@bot.command()
async def graph(ctx, *args):#x_bound:str, y_bound = "", *args):
    in_str = " ".join(args)
    bound_y = r"y ?= ?\(-?[0-9]+\.?[0-9]*, ?-?[0-9]+\.?[0-9]*\)"
    bound_x = r"x ?= ?\(-?[0-9]+\.?[0-9]*, ?-?[0-9]+\.?[0-9]*\)"
    y_bound = re.findall(bound_y, in_str)
    x_bound = re.findall(bound_x, in_str)
    if y_bound:
        in_str = re.sub(bound_y, lambda y: "", in_str)
        y_bounds = tuple(float(y) for y in y_bound[0].replace(" ", "")[3:-1].split(","))
    else:
        y_bounds = None
    if x_bound:
        in_str = re.sub(bound_x, lambda x: "", in_str)
        x_bounds = tuple(float(x) for x in x_bound[0].replace(" ", "")[3:-1].split(","))
    else:
        x_bounds = (-1, 1)
    expr = sympify(in_str.strip(", "))
    expr.subs(Symbol("e"), np.e)
    expr.subs(Symbol("pi"), np.pi)
    expr.subs(Symbol("π"), np.pi)
    f = np.vectorize(lambda x: expr.subs(Symbol("x"), x))
    x = np.linspace(*x_bounds, 1000)
    y = f(x)
    for i, y_elem in enumerate(y):
        try:
            y[i] = float(y[i])
        except:
            y[i] = np.NaN
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set(xlim=x_bounds)
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_visible(False)#.set_color('white') 
    ax.spines['right'].set_visible(False)#.set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.grid(True)
    #ax.axis("equal")
    if y_bounds is not None:
        ax.set(ylim=y_bounds)
    ax.plot(x, y)
    buf = io.BytesIO()
    buf.name = "graph.png"
    fig.savefig(buf, format='png', transparent=True)
    buf.seek(0)
    await ctx.channel.send(file=discord.File(buf))

f = open("maintoken.txt", "r")
token = f.readlines()[0]
bot.run(token)
