from random import randint
from random import choice
import hashlib
from collections import defaultdict

from quack_common import *

description = ""

bot = commands.Bot(command_prefix='?', description=description)

TIMEOUT = 30 * 60

salt = None

@bot.event
async def on_ready():
    global salt
    global vent_channel
    vent_channel = bot.get_channel(vent_id)
    exec(ready)
    try:
        salt = open("vent_salt.txt", "r").read()
    except FileNotFoundError:
        salt_f = open("vent_salt.txt", "w")
        salt = "".join(choice("abcdefghiklmnopqrstuvwxyz0123456789") for _ in range(10))
        salt_f.write(salt)
        salt_f.close()
    while True:
        for channel in subbed:
            if time.time() - session_time[channel.id] > TIMEOUT:
                await channel.send("Session timed out.")
                await end_session(channel)
        await asyncio.sleep(TIMEOUT / 3)


sel_guild = None
sel_channel = None
dm_channel = None

subbed = []
cooldown = defaultdict(lambda: 0)
session_time = defaultdict(lambda: time.time())
forward = defaultdict(lambda: True)
small_ids = defaultdict(lambda: randint(0, 999))
message_duplicates = defaultdict(lambda: [])

admin_ids_live = admin_ids[:]
vent_id = 659559008159531039
vent_channel = None

async def end_session(channel):
    if channel.recipient.id in admin_ids:
        admin_ids_live.append(channel.recipient.id)
    session_time.pop(channel.id, None)
    small_id = small_ids.pop(channel.id, None)
    forward.pop(channel.id, None)
    subbed.remove(channel)
    cooldown[channel.id] = time.time()
    await channel.send(f"Session ended. Please wait 30 seconds to start a new one. To get the same ID next time, paste `{small_id}::{hashlib.md5((salt + str(small_id)).encode()).hexdigest()[:16]}` before sending your next message.")

def process_msg(msg):
    def replace_emoji(match):
        match_str = match.group()
        name = re.sub(r':', '', match_str)
        for emote in bot.get_guild(tech_id).emojis:
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
    pinged_str = re.sub(r'(@[\w ]+#[0-9]{4})|(@\w+)', replace_ping, emojid_str)
    if pinged_str.startswith("> "):
        pinged_str = "\n" + pinged_str
    def replace_channels(match):
        match_str = match.group()
        name = match_str[1:]
        try:
            return f"<#{next(channel.id for channel in sel_guild.channels if channel.name.lower().startswith(name.lower()))}>"
        except (StopIteration, AttributeError):
            return match_str
    return re.sub(r'#(\w|-)+', replace_channels, pinged_str)

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

def extract_id(msg):
    idhash = msg.content.split("::")
    try:
        if 0 <= int(idhash[0]) < 1000:
            hash_str = hashlib.md5((salt + idhash[0]).encode()).hexdigest()[:16]
            if idhash[1] == hash_str:
                return int(idhash[0])
    except ValueError:
        pass
    return None


@bot.event
async def on_message(msg):
    send_id = msg.author.id
    if msg.guild is None and send_id != bot.user.id and send_id not in admin_ids_live:# and bot.get_guild(tech_id).get_member(send_id) is not None:
        if msg.channel not in subbed:
            if time.time() - cooldown[msg.channel.id] < 30:
                await msg.channel.send(f"Please wait {int(30 - time.time() + cooldown[msg.channel.id])} seconds.")
                return
            subbed.append(msg.channel)
            small_id = extract_id(msg)
            if small_id is not None:
                small_ids[msg.channel.id] = small_id
                await msg.channel.send(f"To stop getting messages from venting and support, type `.silent`. To end your session, type `.end`. Session expires after 30 minutes of inactivity. Your ID is {small_ids[msg.channel.id]}.")
                return
            await msg.channel.send(f"To stop getting messages from venting and support, type `.silent`. To end your session, type `.end`. Session expires after 30 minutes of inactivity. Your ID is {small_ids[msg.channel.id]}.")
        if msg.content.lower() in [".end", ".unsub"]:
            await end_session(msg.channel)
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
        t1 = f"**{vent_channel.guild.me.display_name}** (QuackBot#9498): "
        t2 = ""
        sent_msg = await vent_channel.send(f"**{small_ids[msg.channel.id]}**: {process_msg(msg).replace(t1, t2)}", file = file_, files = files)
        message_duplicates[sent_msg.id].append(msg)
        message_duplicates[msg.id].append(sent_msg)
        return
    if msg.channel.id == vent_id:
        file_ = await msg.attachments[0].to_file() if len(msg.attachments) == 1 else None
        files = [await attachment.to_file() for attachment in msg.attachments] if len(msg.attachments) > 1 else None
        for channel in subbed:
            if forward[channel.id] and not msg.content.startswith(f"**{small_ids[channel.id]}**"):
                t1 = f"**{msg.channel.guild.me.display_name}** (QuackBot#9498): "
                t2 = ""
                sent_msg = await channel.send(f"**{msg.author.display_name}** ({msg.author}): {msg.content.replace(t1, t2)}", file = file_, files = files)
                message_duplicates[msg.id].append(sent_msg)
                message_duplicates[sent_msg.id].append(msg)
    #print(f"{msg.author} [{msg.guild}/{msg.channel if msg.guild else None}]: {msg.content}")
    if msg.content.startswith("?restart"):
        if "ventbot".startswith(msg.content[9:]):
            restart_func(send_id)
    global sel_guild
    global sel_channel
    global dm_channel
    if send_id in admin_ids_live:
        if msg.guild == None:
            dm_channel = msg.channel
            if msg.content == "vent":
                admin_ids_live.remove(send_id)
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



bot.run(token)
