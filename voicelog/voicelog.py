import discord
from datetime import datetime
from redbot.core import commands, Config

class VoiceLog(commands.Cog):
    """Loguri pentru voice in-out."""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.allowedguilds = set()
        self.config = Config.get_conf(self, identifier=7669636567)
        self.config.register_guild(enabled=False, channel_id=None)

    async def cog_load(self):
        all_config = await self.config.all_guilds()
        self.allowedguilds = set(guild_id for guild_id, conf in all_config.items() if conf['enabled'])

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild
        if guild.id not in self.allowedguilds:
            return
        if before.channel == after.channel:
            return
        if await self.bot.cog_disabled_in_guild(self, guild):
            return

        embed = discord.Embed(color=member.color, timestamp=datetime.now())
        if not before.channel:
            embed.set_author(name="A intrat", icon_url=member.display_avatar.url)
            embed.description = f"{member.mention} s-a conectat la {after.channel.mention if after.channel else ''}"
        elif not after.channel:
            embed.set_author(name="A iesit", icon_url=member.display_avatar.url)
            embed.description = f"{member.mention} s-a deconectat de la {before.channel.mention}"
        else:
            embed.set_author(name="S-a mutat", icon_url=member.display_avatar.url)
            embed.description = f"{member.mention} s-a mutat de la {before.channel.mention} la {after.channel.mention}"
        
        # If a log channel is configured, try sending there first
        try:
            log_channel_id = await self.config.guild(guild).channel_id()
        except Exception:
            log_channel_id = None

        if log_channel_id:
            log_channel = guild.get_channel(log_channel_id) or self.bot.get_channel(log_channel_id)
            if log_channel:
                perms = log_channel.permissions_for(guild.me)
                if perms.send_messages and perms.embed_links:
                    await log_channel.send(embed=embed)
                    return

        # Fallback: send to the voice channels involved (if permitted)
        for channel in [before.channel, after.channel]:
            if not channel:
                continue
            perms = channel.permissions_for(channel.guild.me)
            if not perms.send_messages or not perms.embed_links:
                continue
            await channel.send(embed=embed)

    @commands.group(invoke_without_command=True)  # type: ignore
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def voicelog(self, ctx: commands.Context):
        """Configurare Voice Log"""
        await ctx.send_help()

    @voicelog.command(name="enable")
    async def voicelog_enable(self, ctx: commands.Context):
        """Porneste logurile pentru voice in-out pentru tot serverul"""
        assert ctx.guild
        self.allowedguilds.add(ctx.guild.id)
        await self.config.guild(ctx.guild).enabled.set(True)
        await ctx.tick(message="Voice Log pornit")

    @voicelog.command(name="disable")
    async def voicelog_disable(self, ctx: commands.Context):
        """Opreste logurile pentru voice in-out pentru tot serverul"""
        assert ctx.guild
        self.allowedguilds.remove(ctx.guild.id)
        await self.config.guild(ctx.guild).enabled.set(False)
        await ctx.tick(message="Voice Log oprit")

    @voicelog.command(name="setchannel")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def voicelog_setchannel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Seteaza canalul unde se trimit logurile. Fara argument sterge setarea."""
        assert ctx.guild
        if channel is None:
            await self.config.guild(ctx.guild).channel_id.set(None)
            await ctx.tick(message="Canalul de log a fost dezactivat")
            return
        await self.config.guild(ctx.guild).channel_id.set(channel.id)
        await ctx.tick(message=f"Canalul de log setat la {channel.mention}")

    @voicelog.command(name="showchannel")
    @commands.guild_only()
    async def voicelog_showchannel(self, ctx: commands.Context):
        """Arata canalul configurat pentru loguri, daca exista."""
        assert ctx.guild
        channel_id = await self.config.guild(ctx.guild).channel_id()
        if not channel_id:
            await ctx.send("Nu este setat niciun canal de log.")
            return
        ch = ctx.guild.get_channel(channel_id) or self.bot.get_channel(channel_id)
        if not ch:
            await ctx.send("Canalul configurat nu este gasit pe server.")
            return
        await ctx.send(f"Canalul de log este: {ch.mention}")
