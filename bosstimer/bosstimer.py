import asyncio
import logging
import discord
import pytz
from datetime import datetime, timedelta
from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.commands import Cog

log = logging.getLogger("red.ursu-cogs.bosstimer")

ROMANIA_TZ = pytz.timezone("Europe/Bucharest")
SPAWN_HOURS = [1, 7, 13, 19]
OFFSETS = [30, 5]


def _get_events_for_date(date):
    events = []
    for hour in SPAWN_HOURS:
        naive = datetime(date.year, date.month, date.day, hour, 0, 0)
        spawn = ROMANIA_TZ.localize(naive, is_dst=None)
        for offset in OFFSETS:
            events.append((spawn - timedelta(minutes=offset), hour, offset))
    return sorted(events)


def _get_next_event(now):
    for delta in range(3):
        for event_time, spawn_hour, offset in _get_events_for_date((now + timedelta(days=delta)).date()):
            if event_time > now:
                return event_time, spawn_hour, offset
    return None


class BossTimer(Cog):
    """Sends boss spawn warnings at 01:00, 07:00, 13:00 and 19:00 Romania time."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=8472910345)
        self.config.register_guild(channel_id=None, role_id=None)
        self._task = bot.loop.create_task(self._timer_loop())

    def cog_unload(self):
        self._task.cancel()

    async def _timer_loop(self):
        await self.bot.wait_until_ready()
        while True:
            try:
                now = datetime.now(ROMANIA_TZ)
                result = _get_next_event(now)
                if not result:
                    await asyncio.sleep(3600)
                    continue
                event_time, spawn_hour, minutes_before = result
                wait = (event_time - now).total_seconds()
                if wait > 0:
                    await asyncio.sleep(wait)
                await self._broadcast(spawn_hour, minutes_before)
            except asyncio.CancelledError:
                break
            except Exception:
                log.exception("Error in boss timer loop")
                await asyncio.sleep(60)

    async def _broadcast(self, spawn_hour: int, minutes_before: int):
        spawn_time_str = f"{spawn_hour:02d}:00"
        for guild in self.bot.guilds:
            data = await self.config.guild(guild).all()
            if not data["channel_id"]:
                continue
            channel = guild.get_channel(data["channel_id"])
            if not channel:
                continue
            role_mention = ""
            if data["role_id"]:
                role = guild.get_role(data["role_id"])
                if role:
                    role_mention = f"{role.mention} "
            if minutes_before == 30:
                msg = f"[{role_mention}] **World boss** spawns in **30 minutes**!"
            else:
                msg = f"[{role_mention}] **World Boss** spawns in **5 minutes**!"
            try:
                await channel.send(msg, allowed_mentions=discord.AllowedMentions(roles=True))
            except Exception:
                log.exception(f"Failed to send boss timer message in guild {guild.id}")

    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def bosstimer(self, ctx: commands.Context):
        """Boss timer configuration commands."""

    @bosstimer.command(name="setchannel")
    async def set_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the channel where boss timer messages will be sent."""
        await self.config.guild(ctx.guild).channel_id.set(channel.id)
        await ctx.send(f"Boss timer channel set to {channel.mention}.")

    @bosstimer.command(name="setrole")
    async def set_role(self, ctx: commands.Context, role: discord.Role):
        """Set the role to mention in boss timer messages."""
        await self.config.guild(ctx.guild).role_id.set(role.id)
        await ctx.send(f"Boss timer role set to {role.mention}.")

    @bosstimer.command(name="clearrole")
    async def clear_role(self, ctx: commands.Context):
        """Remove the role mention from boss timer messages."""
        await self.config.guild(ctx.guild).role_id.set(None)
        await ctx.send("Boss timer role cleared.")

    @bosstimer.command(name="time")
    async def time(self, ctx: commands.Context):
        """Show the current time as seen by the bot (Romania timezone)."""
        now = datetime.now(ROMANIA_TZ)
        await ctx.send(f"🕐 Current time (Romania): **{now.strftime('%Y-%m-%d %H:%M:%S %Z')}**")

    @bosstimer.command(name="status")
    async def status(self, ctx: commands.Context):
        """Show the current boss timer configuration and next event."""
        data = await self.config.guild(ctx.guild).all()
        channel = ctx.guild.get_channel(data["channel_id"]) if data["channel_id"] else None
        role = ctx.guild.get_role(data["role_id"]) if data["role_id"] else None
        now = datetime.now(ROMANIA_TZ)
        result = _get_next_event(now)
        if result:
            event_time, spawn_hour, minutes_before = result
            label = f"{minutes_before}-min warning"
            next_str = f"{label} at **{event_time.strftime('%H:%M')}** (Romania)"
        else:
            next_str = "Unknown"
        embed = discord.Embed(title="Boss Timer Status", color=discord.Color.orange())
        embed.add_field(name="Channel", value=channel.mention if channel else "Not set", inline=True)
        embed.add_field(name="Role", value=role.mention if role else "None", inline=True)
        embed.add_field(name="Next event", value=next_str, inline=False)
        embed.add_field(name="Spawn times", value="01:00 · 07:00 · 13:00 · 19:00 (Romania time)", inline=False)
        await ctx.send(embed=embed)
