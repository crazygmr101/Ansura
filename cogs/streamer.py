from typing import Dict

import discord
from discord.ext import commands

from ansura import AnsuraContext, AnsuraBot
from lib.database import AnsuraDatabase


class Streamer(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot
        self.db: AnsuraDatabase = bot.db
        self.active: Dict[int, int] = {}

    def _add_stream_record(self, guild: discord.Guild):
        self.db.cursor.execute("insert into streamer values (?,?,?,?)", (guild.id, 0, "%user% is streaming!", 0))
        self.db.conn.commit()

    def _edit_stream_record(self, guild: discord.Guild, *, stream_role: int = None, stream_message: str = None,
                            stream_channel: int = None):
        if self._lookup_stream_record(guild=guild) is None:
            self._add_stream_record(guild)
        if stream_role:
            self.db.cursor.execute("update streamer set streamrole=? where guildid=?",
                                   (stream_role, guild.id))
        if stream_message:
            self.db.cursor.execute("update streamer set streammsg=? where guildid=?",
                                   (stream_message, guild.id))
        if stream_channel:
            self.db.cursor.execute("update streamer set streamchannel=? where guildid=?",
                                   (stream_channel, guild.id))
        self.db.conn.commit()

    def _has_stream_record(self, guild: discord.Guild):
        return self._lookup_stream_record(guild) is not None

    def _lookup_stream_record(self, guild: discord.Guild):
        if self.db.cursor.execute("select * from streamer where guildid=?", (guild.id,)).fetchone() is None:
            self._add_stream_record(guild)
        return self.db.cursor.execute("select * from streamer where guildid=?", (guild.id,)).fetchone()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, b: discord.VoiceState, a: discord.VoiceState):
        pass

    @commands.command(aliases=["ssr", "streamrole"])
    @commands.check_any(
        commands.has_permissions(manage_roles=True, manage_guild=True),
        commands.is_owner(),
        commands.has_permissions(administrator=True)
    )
    async def setstreamrole(self, ctx: AnsuraContext, role: discord.Role):
        """
        Sets the streamer role on a server
        """
        self._edit_stream_record(guild=ctx.guild, stream_role=role.id)
        await ctx.send_ok(f"Streamer role set to {role.mention}")

    @setstreamrole.error
    async def setstreamrole_error(self, ctx: AnsuraContext, error: Exception):
        if isinstance(error, discord.ext.commands.ConversionError) or \
                isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send_error("Oops. I can't seem to find that role. Double-check capitalization and spaces.")
        else:
            raise error

    @commands.command(aliases=["ssc", "streamch"])
    @commands.check_any(
        commands.has_permissions(manage_roles=True, manage_guild=True),
        commands.is_owner(),
        commands.has_permissions(administrator=True)
    )
    async def setstreamchannel(self, ctx: AnsuraContext, ch: discord.TextChannel):
        """
        Sets the streamer channel on a server
        """
        self._edit_stream_record(guild=ctx.guild, stream_channel=ch.id)
        await ctx.send_ok(f"Streamer channel set to {ch.mention}")

    @setstreamrole.error
    async def setstreamrole_error(self, ctx: AnsuraContext, error: Exception):
        if isinstance(error, discord.ext.commands.ConversionError) or \
                isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send_error("Oops. I can't seem to find that channel. Double-check capitalization.")
        else:
            raise error

    @commands.command(aliases=["ssm", "streammsg"])
    @commands.check_any(
        commands.has_permissions(manage_roles=True, manage_guild=True),
        commands.is_owner(),
        commands.has_permissions(administrator=True)
    )
    async def setstreammessage(self, ctx: AnsuraContext, *, msg: str):
        """
        Sets the streamer message on a server
        """
        self._edit_stream_record(guild=ctx.guild, stream_message=msg)
        await ctx.send_ok(f"Streamer message set to\n{role.mention}")

    @commands.command(aliases=["gss"])
    async def getstreamsettings(self, ctx: AnsuraContext):
        """
        Gets the streamer role, channel, and message on a server
        """
        rec = self._lookup_stream_record(ctx.guild)
        role, msg, ch = rec[1], rec[2], rec[3]
        await ctx.send(embed=discord.Embed(title=f"Stream info in *{ctx.guild.name}*")
                       .add_field(name="Role", value=f"<@&{role}>" if role != 0 else "Not set")
                       .add_field(name="Message", value=msg)
                       .add_field(name="Channel", value=f"<#{ch}>" if ch != 0 else "Not set"))


def setup(bot):
    bot.add_cog(Streamer(bot))
