import discord
from datetime import datetime, timezone
from redbot.core import commands, Config
from redbot.core.i18n import Translator, cog_i18n

_ = Translator("ClockInOut", __file__)

@cog_i18n(_)
class ClockInOut(commands.Cog):
    """Clock In/Out events"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "clock_in_channel": None,
            "clock_out_channel": None,
        }
        self.config.register_guild(**default_guild)
        self.clock_in_time = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await self.config.guild(member.guild).all()
        # Restul codului on_member_join

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = await self.config.guild(member.guild).all()
        # Restul codului on_member_remove

    @commands.group()
    async def clock(self, ctx):
        """Comenzi pentru înregistrarea orelor de intrare/ieșire"""
        pass

    @clock.command(name="in")
    async def clock_in(self, ctx):
        """Înregistrează intrarea la serviciu"""
        self.clock_in_time = datetime.now(timezone.utc)
        await ctx.send(f"Clock In: {self.clock_in_time.strftime('%H:%M')}")

    @clock.command(name="out")
    async def clock_out(self, ctx):
        """Înregistrează ieșirea de la serviciu și calculează diferența de timp"""
        if not hasattr(self, "clock_in_time") or self.clock_in_time is None:
            await ctx.send("Nu ai înregistrat încă ora de intrare.")
            return
        
        clock_out_time = datetime.now(timezone.utc)
        elapsed_time = clock_out_time - self.clock_in_time
        elapsed_minutes = int(elapsed_time.total_seconds() / 60)
        self.clock_in_time = None
        
        await ctx.send(f"Clock Out: {clock_out_time.strftime('%H:%M')} "
                       f"({elapsed_minutes} minute)")

    @clock.command(name="setchannel")
    async def set_channel(self, ctx, event: str, channel: discord.TextChannel):
        """Configurează canalul pentru evenimentul specificat (intrare/ieșire)"""
        # Restul codului set_channel

    @clock.command(name="resetchannel")
    async def reset_channel(self, ctx, event: str):
        """Resetează canalul pentru evenimentul specificat (intrare/ieșire)"""
        # Restul codului reset_channel