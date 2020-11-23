import requests
from collections.abc import Set
import asyncio

from quack_common import *

# QuackBot has these in quack_common, but you need them for to work

# import discord
# from discord.ext import commands
# import asyncio

description = ""

bot = commands.Bot(command_prefix='?', description=description)

games = {}

@bot.event
async def on_ready():
    # just some prints; you can make this just print "ready" if you want or get
    # get rid of this whole handler without a problem.
    exec(ready)

class TaskManager:
    """
    Allows parallization of asyncio tasks. `TaskManager.dispatch(coroutine)`
    replaces `await coroutine`
    At the end, `await TaskManager()` to await all the tasks.
    """
    def __init__(self):
        self.tasks = []
    def dispatch(self, task):
        self.tasks.append(asyncio.create_task(task))
    async def __call__(self):
        for task in self.tasks:
            await task

class Game:
    def __init__(self, channel):
        self.channel = channel
        self.alive = set(channel.members)
        self.dead = set()
        self.voting = False
    
    def end(self):
        games.pop(self.channel.id)
    
    async def kill(self, members):
        tasks = TaskManager()
        for member in members:
            self.alive.discard(member)
            self.dead.add(member)
            tasks.dispatch(member.edit(deafen=False, mute=self.voting))
        await tasks()

    async def start_vote(self):
        tasks = TaskManager()
        self.voting = True
        for member in self.alive:
            tasks.dispatch(member.edit(deafen=False))
        for member in self.dead:
            tasks.dispatch(member.edit(mute=True))
        await tasks()
    
    async def end_vote(self):
        tasks = TaskManager()
        self.voting = False
        for member in self.alive:
            tasks.dispatch(member.edit(deafen=True))
        for member in self.dead:
            tasks.dispatch(member.edit(mute=False))
        await tasks()

def vc(ctx):
    return ctx.author.voice.channel

def str_members(itr):
    return [str(member) for member in itr]

@bot.command()
async def start_game(ctx):
    channel = vc(ctx)
    if channel is not None:
        games[channel.id] = Game(channel)
        await games[channel.id].end_vote()
        await ctx.send(f"Started game in {channel} with members {str_members(channel.members)}")
    else:
        await ctx.send("You must be in a voice channel.")

@bot.command()
async def end_game(ctx):
    channel = vc(ctx).id
    if channel is None:
        await ctx.send("You must be in a voice channel.")
        return
    game = games[channel]
    game.end()
    await ctx.send("Game ended.")

@bot.command()
async def start_vote(ctx):
    kills = ctx.message.mentions
    channel = vc(ctx).id
    if channel is None:
        await ctx.send("You must be in a voice channel.")
        return
    game = games[channel]
    await game.kill(kills)
    await game.start_vote()
    await ctx.send(f"Started vote with {str_members(kills)} killed. {str_members(game.dead)} are dead.")

@bot.command()
async def end_vote(ctx):
    voted = ctx.message.mentions
    channel = vc(ctx).id
    if channel is None:
        await ctx.send("You must be in a voice channel.")
        return
    game = games[channel]
    if len(voted) == 0:
        await game.end_vote()
        await ctx.send("Ended vote with skip.")
    elif len(voted) == 1:
        game.kill(voted)
        await game.end_vote()
        await ctx.send(f"{voted[0]} was voted out.")
    else:
        await ctx.send("Please only mention 1 member.")
        
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None and before.channel.id in games and after.channel != before.channel:
        game = games[before.channel.id]
        game.alive.discard(member)
        game.dead.discard(member)

bot.run(token) # token variable declared in quack_common—I suggest storing it in
               # in a seperate file and not hardcoding it if you run this yourself