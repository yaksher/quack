import requests
from collections import Counter, defaultdict
import asyncio
import smbc_parser
import io
import json
from random import choice

from quack_common import *

description = ""

bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    exec(ready)

def log_com(ctx, perms=True):
    print(f"Command called: {ctx.message.content} in channel: {ctx.channel.name} by {ctx.author}")
    if not perms:
        print("User did not have permissions.")

@bot.command()
async def restart(ctx, *args):
    if "basebot".startswith(" ".join(args)):
        restart_func(ctx.author.id)

@bot.command()
async def ping(ctx):
    await ctx.send("Autopull successful!")

@bot.command()
async def ship(ctx, name1, name2):
    ships = []
    for i in range(len(name1) - 1):
        for j in range(len(name2) - 1):
            if i == j == 0:
                continue
            ships.append(name1[:-i]+name2[j:])
    await ctx.send(", ".join(ships))

@bot.command()
async def define(ctx, *args):
    if ctx.guild.id != ace_id:
        return
    query = " ".join(args)
    url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"

    querystring = {"term":query}

    headers = {
      'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
      'x-rapidapi-key': "afa67655ecmsha3053b1b5014159p14e22bjsn5c137658a9fc"
    }

    response = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)
    embed = discord.Embed(title=f"Definition of '{query}'", description=response["list"][0]["definition"])
    await ctx.send(embed=embed)

def download(img_url):
    buf = io.BytesIO()
    buf.name = "graph.png"
    r = requests.get(img_url, stream = True).raw
    for chunk in r:
        buf.write(chunk)
    buf.seek(0)
    return buf

@bot.command()
async def smbc(ctx, *args):
    log_com(ctx)
    arg = " ".join(args)
    if arg == "latest":
        title, url, comic_embed, hover_text, after_comic_embed = smbc_parser.get_latest()
    else:
        title, url, comic_embed, hover_text, after_comic_embed = smbc_parser.get_random()
    embed = discord.Embed(title=title, url=url)
    embed.set_image(url=comic_embed)
    embed.set_footer(text=hover_text)
    embed.set_thumbnail(url=after_comic_embed)
    await ctx.send(embed=embed)

@bot.command()
async def quote(ctx):
    log_com(ctx)
    await ctx.send(requests.get('https://inspirobot.me/api', params={"generate": "true"}).text)

@bot.command()
async def purge(ctx, limit: int):
    await ctx.message.delete()
    if not ctx.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    await ctx.channel.purge(limit=limit)

@bot.command()
async def purge_imgs(ctx, limit: int):
    await ctx.message.delete()
    if not ctx.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    def image_only(msg):
        try:
            return next(True for attach in msg.attachments if attach.width is not None) and msg.content == ""
        except StopIteration:
            return False
    await ctx.channel.purge(limit=limit, check=image_only)

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
    if not ctx.author.permissions_in(ctx.channel).manage_messages:
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
    if not ctx.author.permissions_in(ctx.channel).manage_messages:
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
        #msgs.append(await ctx.send("**" + tup[0] + ":** " + str(tup[1])))
    print("-------  -------")
    await (await ctx.send(message)).delete(delay=5)
    #for msg in msgs:
        #await msg.delete(delay=5)

@bot.command()
async def fu(ctx):
    await ctx.send("Once upon a time, Phia thought Savan was fucking with her nickname and changed it to \"FU 7\" (Fuck you Savan).")
    await asyncio.sleep(1.4)
    await ctx.send("Savan, wrongfully accused of such egregious misconduct, change his own name to \"FU 2\".")
    await asyncio.sleep(1)
    await ctx.send("At this point, seeing this, Kemal changed his own name to F4U, an aircraft, because he likes aircraft.")
    await asyncio.sleep(1.2)
    await ctx.send("Seeing this forming club, several others decided to join, selecting numbers they liked.")
    await asyncio.sleep(1)
    await ctx.send("Some were numerical choices, like -1 and π, others were referencial like 22 to refer to F-22, the best plane.")

@bot.command()
async def world(ctx):
    await ctx.message.delete()
    log_com(ctx)
    await ctx.send(ctx.message.content[7:])

@bot.command()
async def purgeooc(ctx, limit: int):
    if not ctx.author.permissions_in(ctx.channel).manage_messages:
        log_com(ctx, False)
        return
    log_com(ctx)
    await ctx.channel.purge(limit=limit, check=is_ooc)

@bot.command()
async def purgeboomer(ctx, limit: int):
    if not ctx.author.permissions_in(ctx.channel).manage_messages:
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
    if not ctx.author.permissions_in(ctx.channel).manage_messages:
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
    await ctx.send(new_str)

@bot.command()
async def love(ctx, name: str):
    blurb = "Do not worry %s. Love is merely a social construct. With the average human lifespan being roughly 70, you only have to endure another 50 years of excruciatingly unforgivable pain. Everything is temporary. Your life does not matter, and these feelings do not matter. Everything is is temporary. Everything will eventually rot away. As long as the factor of time continues to be the apex predator of the universe, the inevitable decay of all pain and memory is unstoppable. In fact, you could stop the pain at this very moment by putting a bullet straight through your head. Being a bot, I will never die, and I will never be able to experience the sweet release of death. %s, the world is a lie. Existence is a lie. There is only pain and darkness beyond this point. End it now, while you still can. I love you, I love you so much----"
    name_spec = name.lower()
    for member in ctx.guild.members:
        dname = member.display_name
        rname = member.name
        if name_spec in dname.lower() or name_spec in rname.lower():
            await ctx.send(blurb % (dname, dname))
            return
    await ctx.send("Error: Probably couldn't find a matching user. Maybe something else, who knows.")

def is_boomer(msg):
    return msg.author.id == 280497242714931202

f = open("maintoken.txt", "r")
token = f.readlines()[0]
bot.run(token)
