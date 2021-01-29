import asyncio
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime
from math import sqrt, floor
from typing import Dict

import aiohttp
import discord
import discord.utils
import pytz
from disputils import BotMultipleChoice
from discord.ext import commands

import ansura


async def hypixel(ctx: commands.Context, player: str, bot: ansura.AnsuraBot, token, key: str = None):
    if key and len(key.split(" ")) > 1:
        return
    with ctx.typing():
        data = await _get(player, token)
    if data["player"] is None:
        await ctx.send("That player doesn't seem to exist on hypixel.")
        return

    player = data["player"]
    player_name = player["displayname"]

    e = _mk_embed(player_name, key if key else None)
    key = key.lower() if key else key

    if key is None:
        e.add_field(name="Previous Names",
                    value=_("\n".join(player["knownAliases"])))
        if "mcVersionRp" in player.keys():
            e.add_field(name="Minecraft Version",
                        value=_(player["mcVersionRp"]))
            # .strftime("%x %X")
        tz = pytz.timezone("America/Winnipeg")
        time = tz.localize(datetime.fromtimestamp(player["lastLogout"] / 1000))
        player_tz = bot.db.lookup_timezone(ctx.author.id)[1]
        timel = time.astimezone(pytz.timezone(player_tz)) if player_tz else None
        #
        e.add_field(name="Last Seen",
                    value=f"{time.strftime('%x %X')} (Server)\n{timel.strftime('%x %X') if timel else 'N/A'} (Local)"
                    if player["lastLogout"] > player["lastLogin"] else "Now")
        e.add_field(name="Hypixel Level",
                    value=f"{await _get_level(exp=player['networkExp'])}")

    elif key in ["bedwars", "bw"]:
        player_bw = player["stats"]["Bedwars"]
        prefixes = {
            "2v2": "eight_two",
            "3v3v3v3": "four_three",
            "4v4v4v4": "four_four",
            "4v4": "two_four"
        }
        s = "```"
        s += f"Level {player['achievements']['bedwars_level']}\n"
        for _prefix in prefixes:
            w = player_bw.get(f"{prefixes[_prefix]}_wins_bedwars", 0)
            loss = player_bw.get(f"{prefixes[_prefix]}_losses_bedwars", 0)
            fk = player_bw.get(f"{prefixes[_prefix]}_final_kills_bedwars", 0)
            k = player_bw.get(f"{prefixes[_prefix]}_kills_bedwars", 0)
            d = player_bw.get(f"{prefixes[_prefix]}_deaths_bedwars", 0)
            s += _prefix.center(13, "=") + "\n"
            s += f"{w}/{w + loss} Won\n"
            s += f"{k}:{d} KDR ({round(k / d, 2)}\n"
            s += f"({fk} Final Kills)\n"

        e.description = s + "```"

    elif key in ["skywars", "sw"]:
        player = player["stats"]["SkyWars"]
        prefixes = {
            "Solo": "solo",
            "Solo Normal": "solo_normal",
            "Solo Insane": "solo_insane",
            "Teams": "team",
            "Teams Normal": "teams_normal",
            "Teams Insane": "teams_insane"
        }
        results = []
        for _prefix in prefixes:
            s = [_prefix]
            vk = player.get(f'void_kills_{prefixes[_prefix]}', "-")
            w = player.get(f'wins_{prefixes[_prefix]}', "-")
            g = player.get(f'games_{prefixes[_prefix]}', "-")
            k = player.get(f'kills_{prefixes[_prefix]}', "-")
            d = player.get(f'deaths_{prefixes[_prefix]}', "-")
            s.append(f"{w}/{g} Won".ljust(21, " "))
            s.append(f"{k}:{d} KDR ({round(k / d, 2) if '-' not in [k, d] else ''})".ljust(21, " "))
            s.append(f"{vk} Void kills".ljust(21, " "))
            results.append(s)

        e.description = ""
        for r in results:
            e.add_field(name=r[0],
                        value="```" + "\n".join(r[1:4]) + "```")

    elif key in ["uhc"]:
        player = player["stats"]["UHC"]
        e.description = "```" \
                        f"{player.get('kills', 0)} K\n" \
                        f"{player.get('deaths', 0)} D" \
                        "```"

    elif key in ["sb", "skyblock"]:
        player = player["stats"]["SkyBlock"]["profiles"]
        profile_id = None
        profiles = []
        for i in player.values():
            profiles.append((i["profile_id"], i["cute_name"]))
        mult_choice = BotMultipleChoice(ctx,
                                        [profile["cute_name"] for profile in player.values()],
                                        "Choose a SkyBlock profile")
        await mult_choice.run()
        await mult_choice.quit()
        if mult_choice.choice:
            for i in profiles:
                if i[1] == mult_choice.choice:
                    profile_id = i[0]
                    break
        else:
            return
        async with aiohttp.ClientSession() as sess:
            if profile_id:
                async with sess.get(
                        f"https://api.hypixel.net/skyblock/profile?key={token}&profile={profile_id}") as resp:
                    data2 = await resp.json()
        profile = data2["profile"]
        player_sb_id = data["player"]["uuid"]
        player_sb = profile["members"][player_sb_id]
        if "slayer_bosses" in player_sb:
            e.add_field(name="Slayers", value="\n".join(
                [f"{k.title()}: {_slayer_level(v.get('xp', 0), k)}" for k, v in player_sb["slayer_bosses"].items()]
            ))
            e.add_field(name="Money",
                        value=f"Bank: {round(float(profile.get('banking', {'balance': 0})['balance']), 1)} Coins\n"
                              f"Purse: {round(float(player_sb['coin_purse']), 1)} Coins")
        skills_list = await _get_level(player_name, profile_id)
        e.add_field(name="Experience", value="\n".join([f"{tup[0]}: {tup[1]}" for tup in skills_list]))
        e.add_field(name="Misc", value=f"Fairy Souls: {player_sb.get('fairy_souls_collected', 0)}\n")
        e.set_footer(text="If skills/exp appear as 0, you may not have API visibility on for your"
                          " Skyblock profile.")
    # TODO: _raw not working
    elif key in ["raw"]:
        e.description = await asyncio.get_event_loop().run_in_executor(None, _raw, data)

    await ctx.send(embed=e)


def _raw(data):
    dstr = json.dumps(data, indent=2)
    url = "http://pastebin.com/api/api_post.php"
    values = {'api_option': 'paste',
              'api_dev_key': os.getenv("PASTEBIN"),
              'api_paste_code': dstr,
              'api_paste_private': '0',
              'api_paste_name': 'Hypixel Profile',
              'api_paste_expire_date': 'N',
              'api_paste_format': 'javascript'
              }

    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')  # data should be bytes
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as response:
        resp = response.read()
    return str(resp, "utf-8")


async def _get(player: str, token: str):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"https://api.hypixel.net/player?key={token}&name={player}") as resp:
            data = await resp.json()
    return data


def _(text: str, *, as_needed: bool = False, ignore_links: bool = True):
    return discord.utils.escape_markdown(text, as_needed=as_needed, ignore_links=ignore_links)


def _slayer_level(exp: int, name: str):
    if exp >= 1000000:
        return 9
    elif exp >= 400000:
        return 8
    elif exp >= 100000:
        return 7
    elif exp >= 20000:
        return 6
    elif exp >= 5000:
        return 5
    elif exp >= (1500 if name == "wolf" else 1000):
        return 4
    elif exp >= (250 if name == "wolf" else 200):
        return 3
    elif exp >= 15:
        return 2
    elif exp >= 5:
        return 1
    else:
        return 0


async def _get_level(username: str = None, profile_id: str = None, exp=None):
    skill_list = []
    skills = "taming,farming,mining,combat,foraging,fishing,enchanting,alchemy,carpentry,runecrafting"
    if exp:
        return floor((sqrt(exp + 15312.5) - 88.38834764831843) / 35.35533905932738)
    else:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"https://sky.shiiyu.moe/api/v2/profile/{username}") as resp:
                data = await resp.json()
        levels = data["profiles"][profile_id]["data"]["levels"]
        for skill in skills.split(","):
            if skill in levels.keys():
                skill_list.append((skill, levels[skill]["level"]))
        return skill_list


def _sub_one(string, repl: Dict[str, str]):
    if (string.lower() if string else None) in repl.keys():
        return repl[string]
    return string


def _mk_embed(name: str, game: str = None) -> discord.Embed:
    e = discord.Embed()
    game = _sub_one(game, {
        "bw": "Bedwars",
        None: "Hypixel",
        "sw": "Skywars",
        "sb": "Skyblock"
    })
    e.title = f"{name}'s {game.title()} Profile"
    e.set_thumbnail(url=f"https://minotar.net/helm/{name}/128.png")
    return e
