import requests
import math as m
from random import randint
from random import choice
from collections import defaultdict

from quack_common import *

description = ""

bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    exec(ready)

change_TSS = True

REACT_PIN_EMOTE_COUNT = 4

previously_pinned = defaultdict(lambda: False)

@bot.event
async def on_raw_reaction_add(payload):
    print("reaction added")
    msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    pin_emote = "📌"
    try:
        pin_react = next(react for react in msg.reactions if react.emoji == pin_emote)
        if pin_react.count < REACT_PIN_EMOTE_COUNT and msg.pinned and not previously_pinned[msg.id]:
            previously_pinned[msg.id] = True
        elif pin_react.count >= REACT_PIN_EMOTE_COUNT:
            await msg.pin()
    except StopIteration:
        pass

@bot.event
async def on_raw_reaction_remove(payload):
    print("reaction removed")
    msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    pin_emote = "📌"
    try:
        pin_react = next(react for react in msg.reactions if react.emoji == pin_emote)
        if pin_react.count < REACT_PIN_EMOTE_COUNT and msg.pinned and not previously_pinned[msg.id]:
            await msg.unpin()
    except StopIteration:
        await msg.unpin()

@bot.event
async def on_message(message):
    global change_TSS
    if message.guild:
        print(message.author, message.content)
    if message.guild and message.guild.id == ace_id:
        if is_boomer(message):
            print("Deleted \"ok boomer\" in channel", message.channel)
            await message.delete()
        messages = await message.channel.purge(limit=5, check=is_boomer)
        if messages != []:
            print(messages, message.channel)
        if is_ooc(message) and message.channel.name != "rp-council":
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
    if message.content == "?restart":
        if "patrolbot".startswith(message.content[9:]):
            restart(message.author.id)
    if message.author.id == yak_id and message.guild is not None:
        role = message.author.roles[-2]
        if message.guild.id == ace_id or role.id == 710307102115102732:
            await role.edit(colour=random_colour())
    for user in message.mentions:
        if user.id == yak_id:
            role = user.roles[-2]
            if message.guild.id == ace_id or role.id == 710307102115102732:
                await role.edit(colour=random_colour())
    content_lower = message.content.lower()
    if re.match(r"(.*yakov.*)|(.*yasha.*)", content_lower):
        for m in message.guild.members:
            if m.id == yak_id:
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


f = open("maintoken.txt", "r")
token = f.readlines()[0]
bot.run(token)
