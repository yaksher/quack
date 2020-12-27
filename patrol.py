import requests
import math as m
from random import randint
from random import choice
from collections import defaultdict
from datetime import datetime

from quack_common import *

description = ""

bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    exec(ready)

REACT_PIN_EMOTE_COUNT = 4
pin_emote = "📌"
pinboard_emote = "⭐"

previously_pinned = defaultdict(lambda: False)

@bot.event
async def on_raw_reaction_add(payload):
    async def pinboard(msg):
        pinboard_channel = bot.get_channel(prefs.guilds[msg.guild.id]["pinboard"])
        embed = discord.Embed(description=f"{msg.content}\n\n\n{msg.author.mention}\nhttps://discord.com/channels/{msg.guild.id}/{msg.channel.id}/{msg.id}")
        embed.set_author(name=f"{msg.author.name} in #{msg.channel}", icon_url=msg.author.avatar_url)
        if len(msg.attachments) != 0:
            embed.set_image(url=msg.attachments[0].url)
        await pinboard_channel.send(embed=embed)

    if payload.emoji.name == pin_emote:
        msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        try:
            react = next(react for react in msg.reactions if react.emoji == pin_emote)
            if react.count < REACT_PIN_EMOTE_COUNT and msg.pinned and not previously_pinned[msg.id]:
                previously_pinned[msg.id] = True
            elif react.count >= REACT_PIN_EMOTE_COUNT:
                await msg.pin()
        except StopIteration:
            pass
    elif payload.emoji.name == pinboard_emote:
        msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if prefs[msg.guild.id]["pinboard"] is None:
            return
        try:
            react = next(react for react in msg.reactions if react.emoji == pinboard_emote)
            if react.count == prefs[msg.guild.id]["emote_count"]:
                await pinboard(msg)
        except StopIteration:
            pass


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.emoji != pin_emote:
        return
    msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    try:
        react = next(react for react in msg.reactions if react.emoji == pin_emote)
        if react.count < REACT_PIN_EMOTE_COUNT and msg.pinned and not previously_pinned[msg.id]:
            await msg.unpin()
    except StopIteration:
        if msg.pinned and not previously_pinned[msg.id]:
            await msg.unpin()

change_TSS = True

class TaskManager:
    def __init__(self):
        self.tasks = []
    def dispatch(self, func, *args, **kwargs):
        self.tasks.append(asyncio.create_task(func(*args, **kwargs)))
    async def __call__(self):
        for task in self.tasks:
            await task

@bot.event
async def on_message(msg):
    if msg.content == "?ping":
        received = datetime.utcnow().timestamp()
        pong1 = "Server to bot: {:.1f}ms".format((received - msg.created_at.timestamp()) * 1000)
        pong_msg = await msg.channel.send(pong1)
        pong2 = "{}\nBot to server: {:.1f}ms".format(pong1, (datetime.utcnow().timestamp() - pong_msg.created_at.timestamp()) * 1000)
        await pong_msg.edit(content=pong2)
    global change_TSS
    tasks = TaskManager()
    hell_id = 107490019710615552
    send = msg.channel.send
    if msg.guild and msg.guild.id == ace_id:
        if re.match(r".*clab.*", msg.content.lower()) and msg.author.id == hell_id:
            tasks.dispatch(send, "https://cdn.discordapp.com/attachments/589292970541318185/751616703238242387/Hold_it_thats_mega_cringe-1.mp4")
        if is_boomer(msg):
            print("Deleted \"ok boomer\" in channel", msg.channel)
            tasks.dispatch(msg.delete)
        if is_ooc(msg):
            print("Moved OOC msg from channel", msg.channel)
            ooc_channel = bot.get_channel(509541675765465108)
            tasks.dispatch(ooc_channel.send, "**[%s] %s:** %s" % (msg.channel.name[3:], str(msg.author.display_name), trim_ooc(process_pings(msg))))
            tasks.dispatch(msg.delete, delay=10)
        TSS_ID = 207642057198534656
        if msg.author.id == TSS_ID:
            if change_TSS:
                change_TSS = False
                get_nick = getNick()
                tasks.dispatch(msg.author.edit, nick=get_nick[0])
        else:
            change_TSS = True
        for user in msg.mentions:
            if user.id == TSS_ID:
                get_nick = getNick()
                tasks.dispatch(user.edit, nick=get_nick[0])
        if tssName(msg.content):
            for m in msg.guild.members:
                if m.id == TSS_ID:
                    tasks.dispatch(m.edit, nick=tssName(msg.content))
        if is_hal_summon(msg.content):
            async def summon_hal():
                ping = await send("<@!381597229644775425>")
                await ping.delete()
            tasks.dispatch(summon_hal)

    if msg.content == "&quote":
        tasks.dispatch(send, requests.get('https://inspirobot.me/api', params={"generate": "true"}).text)
    if msg.content == "?restart":
        if "patrolbot".startswith(msg.content[9:]):
            restart_func(msg.author.id)
    if msg.author.id == yak_id and msg.guild is not None:
        role = msg.author.roles[-2]
        if msg.guild.id == ace_id or role.id == 710307102115102732:
            tasks.dispatch(role.edit, colour=random_colour())
    for user in msg.mentions:
        if user.id == yak_id:
            role = user.roles[-2]
            if msg.guild.id == ace_id or role.id == 710307102115102732:
                tasks.dispatch(role.edit, colour=random_colour())
    content_lower = msg.content.lower()
    if re.match(r"(.*yakov.*)|(.*yasha.*)", content_lower):
        if msg.guild is not None:
            for m in msg.guild.members:
                if m.id == yak_id:
                    role = m.roles[-2]
                    if msg.guild.id == ace_id or role.id == 710307102115102732:
                        tasks.dispatch(role.edit, colour=random_colour())
    await tasks()

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

bot.run(token)
