import discord
from discord.ext import commands
import re, sys, os, io
import requests
from random import choice

description = ""

bot = commands.Bot(command_prefix='>', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(activity=discord.Game(name="with my Bonking stick"))
    print('------')

hugPics = [
  "https://cdn.discordapp.com/attachments/678715301222809641/736415604428505099/Untitled-2.png",
  "https://cdn.discordapp.com/attachments/678715301222809641/736415742991532112/095a521d-e2b1-430d-8cca-6d5a0c4c6754.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736418579695796274/image0.jpg",
  "https://cdn.discordapp.com/attachments/664275859317850175/736418823393116250/2Q.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736418857207595058/image0.jpg",
  "https://cdn.discordapp.com/attachments/664275859317850175/736418865353064558/2Q.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736418910185979974/9k.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736418952699314206/2Q.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419004897558618/9k.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419089245012058/images.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419089236492398/image0.jpg",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419187265896498/2Q.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419206563627169/image0.jpg",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419318362800159/8_021215035025.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419332568907786/image0.jpg",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419397865963570/7_021215035025.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419483039694888/image0.jpg",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419615726370977/2_021215034916.png",
  "https://cdn.discordapp.com/attachments/664275859317850175/736419866965311568/image0.jpg"]
honkPics = [
  "https://cdn.discordapp.com/attachments/659440262422069272/737713310799101972/medium_honk.jpg",
  "https://cdn.discordapp.com/attachments/659440262422069272/737714573519487068/image.png",
  "https://cdn.discordapp.com/attachments/659440262422069272/737714051731161168/tenor.gif",
  "https://cdn.discordapp.com/attachments/659440262422069272/737711858202574858/OIP.png"]

def download(img_url):
    buf = io.BytesIO()
    buf.name = "graph.png"
    r = requests.get(img_url, stream = True).raw
    for chunk in r:
        buf.write(chunk)
    buf.seek(0)
    return buf

from datetime import *
@bot.event
async def on_message(msg):
    if msg.content == ";ping":
        received = datetime.utcnow().timestamp()
        await msg.channel.send("Server to bot: {:.1f}ms".format((received - msg.created_at.timestamp()) * 1000))
        await msg.channel.send("Bot to server: {:.1f}ms".format(bot.latency * 1000))
    msg_lower = msg.content.lower()
    if msg_lower == "restart" and msg.author.id == 735279544524603493:
        os.system("git pull")
        os.execl(sys.executable, sys.executable, *sys.argv)
    blacklist_ids = [735279544524603493, 735271620658200606]
    if msg.author.id in blacklist_ids:
        return
    ping = re.search(r"<@!?[0-9]{18}>", msg_lower)
    if ping is None:
        return
    ping = ping.group(0)
    if "hug" in msg_lower:
        img_url = choice(hugPics)
        img = discord.File(download(img_url))
        await msg.channel.send(f"{msg.author.mention} has sent a hug to {ping}!", file = img)
        return
    if "hard" in msg_lower:
        hard = True
    else:
        hard = False
    bonktype = None
    if "luvbonk" in msg_lower:
        img_url = "https://cdn.discordapp.com/attachments/659560407807033364/735598299033108510/luvbonk-transparent.png"
        bonktype = "luvbonk"
    elif "luvhonk" in msg_lower:
        img_url = choice(honkPics)
        bonktype = "luvhonk"
    elif "honk" in msg_lower:
        img_url = choice(honkPics)
        bonktype = "honk"
    elif "horny" in msg_lower or "jail" in msg_lower:
        img_url = "https://cdn.discordapp.com/attachments/661806248223834113/739557065462251530/tenor.gif"
        bonktype = "horny jail"
    elif "bonk" in msg_lower:
        img_url = "https://cdn.discordapp.com/attachments/659560407807033364/735597799743422605/bonk-transparent.png"
        bonktype = "bonk"
    if bonktype is None:
        return
    img = discord.File(download(img_url))
    hard_str = " hard" if hard else ""
    if "438821323959959562" in ping:
        await msg.channel.send(f"{msg.author.mention} tries to {bonktype} {ping}{hard_str}\nYou have {bonktype}ed the creator, so in return, <@!438821323959959562> {bonktype}s {msg.author.mention}.", file=img)
    else:
        await msg.channel.send(f"{msg.author.mention} {bonktype}s {ping}{hard_str}", file = img)

f = open("bonktoken.txt", "r")
token = f.readlines()[0]
bot.run(token)