import random
import re
from typing import List, Union

import discord
from discord.ext import commands

import cogs
from ansura import AnsuraBot, AnsuraContext


class Owner(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot
        self.guilds: List[discord.Guild] = []

    @commands.command()
    @commands.is_owner()
    async def setgame(self, ctx: AnsuraContext, status: str):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(status))

    @commands.command()
    @commands.is_owner()
    @commands.has_permissions(manage_guild=True, manage_nicknames=True)
    @commands.bot_has_permissions(manage_guild=True, manage_nicknames=True)
    async def nick_all(self, ctx: AnsuraContext, name: str):
        """
        Nickname all users in a server according to a pattern
        <join-num100> - 3 digit padded join num
        <join-num>
        <joined> - timestamp of user join
        <disc>
        <name>
        """
        await ctx.send("Nicknaming " + str())
        g: discord.Guild = ctx.guild
        s = 0
        f = 0
        i: Union[discord.Member, discord.User]
        a: List[Union[discord.Member, discord.User]] = [x for x in g.members]
        a.sort(key=lambda x: x.joined_at)
        c = 0
        for i in a:
            c += 1
            try:
                s += 1
                n = name
                n = re.sub(r"<join-num100>", str(c).zfill(3), n)
                n = re.sub(r"<join-num>", str(c), n)
                n = re.sub(r"<joined>", str(i.joined_at), n)
                n = re.sub(r"<disc>", str(i.discriminator), n)
                n = re.sub(r"<name>", str(i.name), n)
                await i.edit(nick=n)
            except:
                f += 1
                pass
        await ctx.send("Nicked " + str(s) + " (" + str(f) + " failed)")

    @commands.command()
    @commands.is_owner()
    @commands.has_permissions(manage_guild=True, manage_nicknames=True)
    @commands.bot_has_permissions(manage_guild=True, manage_nicknames=True)
    async def shufflenicks(self, ctx: AnsuraContext):
        """
        Shuffle the nicknames of all users in a server
        """
        g = ctx.guild
        a: List[Union[discord.Member, discord.User]] = [x for x in g.members]
        b: List[Union[discord.Member, discord.User]] = [x for x in g.members]
        random.shuffle(a)
        for u in range(len(b)):
            try:
                await b[u].edit(nick=a[u].name)
                print(b[u].name + " , " + b[u].nick)
            except:
                pass

    @commands.command()
    @commands.is_owner()
    @commands.has_permissions(manage_guild=True, manage_roles=True)
    @commands.bot_has_permissions(manage_guild=True, manage_roles=True)
    async def role_all(self, ctx: AnsuraContext, role: discord.Role):
        """
        Gives a role to all members of a server
        - role: the role to give a user
        """
        g: discord.Guild = ctx.guild
        s = 0
        f = 0
        r = role
        i: Union[discord.Member, discord.User]
        a: List[Union[discord.Member, discord.User]] = [x for x in g.members]
        await ctx.send("Giving everyone  " + r.mention)
        c = 0
        for i in a:
            c += 1
            try:
                await i.add_roles(r)
                print("Added to " + str(i.display_name))
            except Exception as e:
                f += 1
                print("Failed on " + str(i.display_name))
                print(e)
                pass
        await ctx.send("Gave " + r.mention + " to " + str(s) + " (" + str(f) + " failed)")

    @commands.command()
    @commands.is_owner()
    async def guilds(self, ctx: AnsuraContext):
        tts: cogs.voice.TTS = self.bot.get_cog("TTS")
        g: discord.Guild
        m: discord.Message = await ctx.send("Building list...")
        s = """```"""
        async with ctx.typing():
            for g in self.bot.guilds:
                s += f"{g.id} - {g.name}\n"
        await m.edit(content=s + "```")

    @commands.command()
    @commands.is_owner()
    async def ginfo(self, ctx: AnsuraContext, guild_id: int):
        async with ctx.typing():
            if guild_id not in [g.id for g in self.bot.guilds]:
                await ctx.send("I'm not in a guild with that ID")
                return
            m: discord.User
            g: discord.Guild = self.bot.get_guild(guild_id)
            users, bots = 0, 0
            for m in g.members:
                if m.bot:
                    bots += 1
                else:
                    users += 1
            e = discord.Embed()
            e.title = g.name
            e.set_thumbnail(url=g.icon_url)
            e.description = g.description
            e.add_field(name="Total Members", value=g.member_count)
            e.add_field(name="Users/Bots", value=f"{users}/{bots}")
            e.add_field(name="Region", value=str(g.region))
            e.add_field(name="ID", value=str(g.id), inline=False)
            u: discord.User = g.owner
            e.add_field(name="Owner", value=f"{u.name}#{u.discriminator} ({g.owner_id})", inline=False)
        await ctx.send(embed=e)

    @commands.command()
    @commands.is_owner()
    async def guild_leave(self, ctx: AnsuraContext, id: int):
        """Leaves a guild given by <id>"""
        g: discord.Guild = self.bot.get_guild(id)
        if g is None:
            await ctx.send("I'm not in a guild with this ID")
            return
        s = g.name
        await g.leave()
        await ctx.send(f"Left {s}")

    @commands.command()
    @commands.is_owner()
    async def die(self, ctx: AnsuraContext):
        await ctx.send_ok(random.choice([
            "Oh..okay..sure..I'll brb",
            "): Okay",
            "D: But..why? *sighs* fInE"
        ]))
        exit()


def setup(bot):
    bot.add_cog(Owner(bot))
