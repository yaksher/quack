from quack_common import *

import requests
from collections import Counter, defaultdict

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
async def servercounts(ctx, *args):
    try:
        await ctx.message.delete()
    except discord.errors.Forbidden:
        pass
    blacklist_ids = [int(arg) for arg in args]
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
        if type(channel) is discord.TextChannel and channel.id not in blacklist_ids:
            tasks.append(asyncio.create_task(download(channel)))
    tasks_rem[0] = len(tasks)
    for task in tasks:
        await task
    print("-------  -------")
    p_list = [(k, v, v / message_counts[k]) for k, v in counts.items() if v >= 10]
    p_list.sort(key=lambda tup: tup[1])
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

from math import ceil
@bot.command()
async def emote_counts(ctx):
    log_com(ctx)
    if ctx.author.id != yak_id:
        return
    emote_counts = {emoji.id: 0 for emoji in ctx.guild.emojis if not emoji.animated}
    async def download(channel):
        print(f"started: {channel.name}")
        try:
            async for msg in channel.history(limit=None):
                emoji_strs = re.findall(r'<:\w+:[0-9]{18}>', msg.content)
                emoji_ids = [int(re.search(r'[0-9]{18}', s).group()) for s in emoji_strs]
                for emoji_id in emoji_ids:
                    if emoji_id in emote_counts:
                        emote_counts[emoji_id] += 1
                for react in msg.reactions:
                    if type(react.emoji) is not str and react.emoji.id in emote_counts:
                        emote_counts[react.emoji.id] += react.count
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
    sorted_ids = sorted(emote_counts.keys(), key=lambda x: emote_counts[x], reverse=True)
    lines = [f"{next(emoji for emoji in ctx.guild.emojis if emoji.id == emoji_id)}: {emote_counts[emoji_id]}" for emoji_id in sorted_ids]
    outputs = ["\n".join(lines[i*50:(i+1)*50]) for i in range(ceil(len(lines)/50))]
    for i, out in enumerate(outputs):
        embed = discord.Embed(title=f"Emote counts ({i + 1}/{len(outputs)})", description=out)
        await ctx.send(embed=embed)

class TaskManager:
    def __init__(self):
        self.tasks = []
    def dispatch(self, task):
        self.tasks.append(asyncio.create_task(task))
    async def __call__(self):
        for task in self.tasks:
            await task

@bot.command()
async def recover_starboard(ctx):
    log_com(ctx)
    if ctx.author.id != yak_id:
        return

    async def pinboard(msg):
        pinboard_channel = bot.get_channel(prefs.guilds[msg.guild.id]["pinboard"])
        embed = discord.Embed(description=f"{msg.content}\n\n\nhttps://discord.com/channels/{msg.guild.id}/{msg.channel.id}/{msg.id}")
        embed.set_author(name=f"{msg.author.name} in {msg.channel}", icon_url=msg.author.avatar_url)
        if len(msg.attachments) != 0:
            embed.set_image(url=msg.attachments[0].url)
        await pinboard_channel.send(embed=embed)
    async def download(channel):
        print(f"started: {channel.name}")
        try:
            tasks = TaskManager()
            async for msg in channel.history(limit=None, oldest_first=True):
                for react in msg.reactions:
                    if react.emoji == "🌟":
                        tasks.dispatch(pinboard(msg))
                        break
            await tasks()
        except discord.errors.Forbidden:
                pass
        tasks_rem[0] -= 1
        print(f"finished: {channel.name} | remaining {tasks_rem[0]}")
    tasks_rem = [0]
    downloads = TaskManager()
    for channel in ctx.guild.channels:
        if type(channel) is discord.TextChannel:
            downloads.dispatch(download(channel))
    tasks_rem[0] = len(downloads.tasks)
    await downloads()


f = open("maintoken.txt", "r")
token = f.readlines()[0]
bot.run(token)