import os, sys
import discord
import re
from discord.ext import commands
import io
import asyncio
import time
import pickle

tech_id = 659440262422069269
ace_id = 463225414534430721
emotes_id = 750971097054445648

yak_id = 133270838605643776
slav_id = 193701039633989632
admin_ids = [yak_id, slav_id]

ready = """print('Logged in as')
print(bot.user.name)
print(bot.user.id)
print(" ".join(sys.argv))
print('------')"""

def restart_func(user_id):
    if user_id in admin_ids:
        os.execl(sys.executable, sys.executable, *sys.argv)

token = open("maintoken.txt", "r").read()

pref_file = "preferences.pickle"

class QuackPrefs:
    def __init__(self, save_filename):
        self.save_filename = save_filename
        self.last_updated = time.time()
        self.load()

    def set_prefs(self, guild_id, prefs):
        self.load_checked()
        if guild_id not in self.guilds:
            self.guilds[guild_id] = {}
        self.guilds[guild_id].update(prefs)
        self.save()
    
    def __setitem__(self, guild_id, prefs):
        self.load_checked()
        if guild_id not in self.guilds:
            self.guilds[guild_id] = {}
        self.guilds[guild_id] = prefs
        self.save()

    def get_pref(self, guild_id, pref):
        self.load_checked()
        if guild_id not in self.guilds or pref not in self.guilds[guild_id]:
            return None
        return self.guilds[guild_id][pref]

    def __getitem__(self, guild_id):
        self.load_checked()
        if guild_id not in self.guilds:
            self.guilds[guild_id] = {}

        class GetRetObject():
            def __init__(self, parent, guild_id):
                self.prefs = parent.guilds[guild_id]
                self.parent = parent
                self.guild_id = guild_id
            def __setitem__(self, pref, val):
                self.parent.load_checked()
                self.prefs[pref] = val
                self.parent.save()
            def __getitem__(self, pref):
                self.parent.load_checked()
                if pref not in self.prefs:
                    return None
                return self.prefs[pref]
            def update(self, prefs):
                self.parent.load_checked()
                self.prefs.update(prefs)
                self.parent.save()
            def __iadd__(self, prefs):
                self.update(prefs)
                return self.parent.guilds[self.guild_id]

        return GetRetObject(self, guild_id)

    def load_checked(self):
        last_modified = os.path.getmtime(self.save_filename)
        if last_modified > self.last_updated:
            self.load()

    def load(self):
        try:
            self.guilds = pickle.load(open(self.save_filename, "rb"))
        except FileNotFoundError:
            self.guilds = {}
            self.save()
        self.last_updated = time.time()

    def save(self):
        pickle.dump(self.guilds, open(self.save_filename, "wb"))

prefs = QuackPrefs(pref_file)
