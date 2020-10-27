import glob
import logging
import os
import random
import re

import discord
import dotenv
from discord.ext import commands

import cogs
from ansura import AnsuraBot
from cogs.crosschat import Crosschat
from lib.voicemanager import VoiceManager

logging.basicConfig(level=logging.WARN)

dotenv.load_dotenv(".env")


def get_prefix(bot, message):
    return commands.when_mentioned_or("%")(bot, message)


bot = AnsuraBot(command_prefix=get_prefix)
bot.remove_command('help')

bot.vm = VoiceManager(bot)

initial_extensions = ['cogs.gamertags',
                      'cogs.administration',
                      'cogs.misc',
                      'cogs.gaming',
                      'cogs.fun',
                      'cogs.owner',
                      'cogs.image',
                      'cogs.error-handler',
                      'cogs.streamer',
                      'cogs.confighandler',
                      'cogs.timezones',
                      'cogs.voice',
                      'cogs.help',
                      'cogs.crosschat']
if __name__ == '__main__':
    for ext in initial_extensions:
        print(f"[COGS] Loading {ext}")
        bot.load_extension(ext)

filelist = glob.glob("*.mp3")
for file in filelist:
    try:
        os.remove(file)
    except:
        print(f"err removing {file}")
filelist = glob.glob("attachments/*")
for file in filelist:
    try:
        os.remove(file)
    except:
        print(f"err removing {file}")


@bot.event
async def on_ready():
    if bot.user.id == 603640674234925107:
        import cogs.dbl
        await bot.add_cog(cogs.dbl.DBL(bot))

    xchat: Crosschat = bot.get_cog("Crosschat")
    await xchat.init_channels()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("%help"))
    await bot.cfg.start()
    print("Ansura online! :D")
    print(f" {len(bot.guilds)} Guilds")


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    guild: discord.Guild = before.guild
    if not (discord.Streaming in [type(x) for x in after.activities] and
            discord.Streaming not in [type(x) for x in before.activities]):
        return
    streamer: cogs.streamer.Streamer = bot.get_cog("Streamer")
    rec = streamer._lookup_stream_record(guild)
    if rec is None: return
    if rec[1] == 0 or rec[3] == 0: return
    if rec[1] in [r.id for r in before.roles]:
        channel = guild.get_channel(rec[3])
        s: discord.Streaming
        for a in after.activities:
            if type(a) is discord.Streaming:
                s = a
                break
        msg = re.sub("%user.mention%", after.mention, rec[2])
        msg = re.sub("%user%", after.display_name, msg)
        msg = re.sub("%url%", s.url, msg)
        await channel.send(msg)



bot.run(os.getenv("ANSURA"))
