import itertools
import math
import random

import discord
import requests
from discord.ext import commands

from ansura import AnsuraBot, AnsuraContext


class Fun(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot

    @commands.command()
    async def ship(self, ctx: AnsuraContext, user1: discord.Member, user2: discord.Member):
        """Ships two users.. awww <3"""
        name1: str = user1.display_name
        name2: str = user2.display_name

        def split(s: str):
            import re
            if s == "crazygmr101":
                return ["crazy", "gmr101"]
            if len(s.split(" ")) > 1:
                ar = s.split(" ")
                return [
                    " ".join(ar[:math.floor(len(s.split(" ")) / 2)]),
                    " ".join(ar[math.floor(len(s.split(" ")) / 2):])
                ]
            if len(s.split("_")) > 1:
                ar = s.split("_")
                return [
                    " ".join(ar[:1]),
                    " ".join(ar[1:])
                ]
            # check for alt caps
            ar = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', s)).split()
            if len(ar) > 1:
                return [
                    " ".join(ar[:1]),
                    " ".join(ar[1:])
                ]
            # TODO: work on this code a tad more, just push
            half = int(len(s) / 2)
            return [s[:half], s[half:]]

        await ctx.send_info("I ship it: " + split(name1)[0] + split(name2)[1])

    @commands.command()
    async def hug(self, ctx: AnsuraContext, user: discord.Member):
        """Hug a user"""
        await ctx.embed(
            description=f'{ctx.author.mention} hugs {user.mention}',
            image=requests.get("https://nekos.life/api/v2/img/hug").json()["url"]
        )

    @commands.command()
    async def pat(self, ctx: AnsuraContext, user: discord.Member):
        """Pat a user"""
        await ctx.embed(
            description=f'{ctx.author.mention} pats {user.mention}',
            image=requests.get("https://nekos.life/api/v2/img/pat").json()["url"]
        )

    @commands.command()
    async def poke(self, ctx: AnsuraContext, user: discord.Member):
        """Poke a user"""
        await ctx.embed(
            description=f'{ctx.author.mention} pokes {user.mention}',
            image=requests.get("https://nekos.life/api/v2/img/poke").json()["url"]
        )

    @commands.command()
    async def cuddle(self, ctx: AnsuraContext, user: discord.Member):
        """Cuddle a user"""
        await ctx.embed(
            description=f'{ctx.author.mention} cuddles {user.mention}',
            image=requests.get("https://nekos.life/api/v2/img/cuddle").json()["url"]
        )

    @commands.command()
    async def kiss(self, ctx: AnsuraContext, user: discord.Member):
        """Kiss a user"""
        await ctx.embed(
            description=f'{ctx.author.mention} kisses {user.mention}',
            image=requests.get("https://nekos.life/api/v2/img/kiss").json()["url"]
        )

    @commands.command(aliases=["bork"])
    async def woof(self, ctx: AnsuraContext):
        """Sends a dog pic"""
        images = [
            "irXVvTn", "1Hy1Ivm", "snyoQYt", "iTD3btm", "gI2hJgp", "4JW8iDZ", "71ssqGq", "WjNBjzO", "LQOkhKM",
            "eVFf6Oy", "JL4jVlG", "C4E5iAl", "Ck08zJG", "k18Raxy", "aJG7iXc", "CThNFi4", "jg2zL7E", "DaHdglt",
            "FRstrnz", "0HrTq3Y", "ZK7VcJN", "8lPbfAJ", "E7dje1b", "1Hy1Ivm"
        ]
        discord.Embed()
        woof_text = random.choice(["Woof!", "Arf!", "Bork!"])
        woof_emoji = random.choice(["▼・ᴥ・▼", "▼(´ᴥ`)▼", "U ´ᴥ` U", "U・ᴥ・U", "U・ﻌ・U", "U ´x` U", "(U・x・U)",
                                    "υ´• ﻌ •`υ", "૮ ・ﻌ・ა", "(❍ᴥ❍ʋ)", "( ͡° ᴥ ͡° ʋ)", "V●ω●V", "V✪ω✪V", "V✪⋏✪V",
                                    "∪ ̿–⋏ ̿–∪", "∪･ω･∪", "໒( ●ܫฺ ●)ʋ", "໒( = ᴥ =)ʋ}"])
        woof_img = random.choice(images)
        await ctx.embed(
            image=f"https://i.imgur.com/{woof_img}.jpg",
            title=f'{woof_text} {woof_emoji}'
        )

    @commands.command()
    async def meow(self, ctx: AnsuraContext):
        """Sends a cat pic"""
        discord.Embed()
        meow_text = random.choice(["(^-人-^)", "(^・ω・^ )", "(=;ェ;=)", "(=^・^=)", "(=^・ｪ・^=)", "(=^‥^=)", "(=ＴェＴ=)",
                                   "(=ｘェｘ=)", "＼(=^‥^)/`", "~(=^‥^)/", "└(=^‥^=)┐", "ヾ(=ﾟ・ﾟ=)ﾉ", "ヽ(=^・ω・^=)丿",
                                   "d(=^・ω・^=)b", "o(^・x・^)o"])
        await ctx.embed(
            title=f"Meow {meow_text}",
            image=requests.get("https://nekos.life/api/v2/img/meow").json()["url"]
        )

    @commands.command(aliases=["pbc", "chicken"])
    async def placeblock_chicken(self, ctx: AnsuraContext):
        """Does a Maddie"""
        await ctx.send(random.choice("🐔,🐤,🐥,🐣".split(",")))

    @commands.command()
    async def maddify(self, ctx: AnsuraContext):
        """Vöïds a message"""
        discord.Embed()
        msg: str = ctx.message.content
        msg_o: discord.Message = ctx.message
        msg = " ".join(msg.split(" ")[1::])
        replacements = [
            "a,e,i,o,u,A,E,I,O,U".split(","),
            "ä,ë,ï,ö,ü,Ä,Ë,Ï,Ö,Ü".split(",")
        ]
        for i in range(len(replacements[0])):
            msg = msg.replace(replacements[0][i], replacements[1][i])
        await ctx.send_info(msg)
        await msg_o.delete()

    @commands.command()
    async def colorcodes(self, ctx: AnsuraContext):
        """
        Shows minecraft color and formatting codes
        """
        url = "https://gamepedia.cursecdn.com/minecraft_gamepedia/thumb/7/7e/Minecraft_Formatting.gif/" \
              "200px-Minecraft_Formatting.gif?version=14d34015f6cdd3412acabdd0d80764d9"

        await ctx.send(embed=discord.Embed(
            title="Minecraft Color Codes",
            url="https://minecraft.gamepedia.com/Formatting_codes",
            description=""
                        "To type `§`:\n"
                        "- Windows: `Alt`+`21`, or `Alt`+`0167`, using the numpad\n"
                        "- Mac (US): `Option`+`6` (`5` for US Extended)\n"
                        "- Mac (Other): `Option`+`00a7`\n"
                        "- Linux: `Compose` `s` `o` or `Ctrl` +`Shift` + `u00a7`\n\n"
                        "[Color code list](https://minecraft.gamepedia.com/Formatting_codes#Color_codes)"
        ).set_image(url=url))

    @commands.command(aliases=["ccpattern"])
    async def colorcodepattern(self, ctx: AnsuraContext, pattern: str, *, text: str):
        """
        Colors a text according to a predefined or custom pattern, to copy and paste in to plugins that support & syntax
        """
        # §0 	black
        # §1 	dark_blue
        # §2 	dark_green
        # §3 	dark_aqua
        # §4 	dark_red
        # §5 	dark_purple
        # §6 	gold
        # §7 	gray
        # §8 	dark_gray
        # §9 	blue
        # §a 	green
        # §b 	aqua
        # §c 	red
        # §d 	light_purple
        # §e 	yellow
        # §f 	white
        # §k 	Obfuscated
        # §l 	Bold
        # §m 	Strikethrough
        # §n 	Underline
        # §o 	Italic
        # §r 	Reset
        patterns = {
            "rainbow": "c6ea15"
        }
        if pattern in patterns:
            pattern = patterns[pattern]
        pattern_list = pattern.split(",") if "," in pattern else [char for char in pattern]
        cycle = itertools.cycle(pattern_list)
        builder = ''
        for char in text:
            if char.isspace():
                builder += char
            else:
                for formatting_code in cycle.__next__():
                    builder += f"&{formatting_code}"
                builder += char
        await ctx.send(f"```{builder}```{'**Over 256 characters' if len(builder) > 256 else ''}")


def setup(bot):
    bot.add_cog(Fun(bot))
