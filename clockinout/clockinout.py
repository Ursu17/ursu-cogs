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
        await ctx.send(f"{ctx.author.mention} a înregistrat ora de intrare: {self.clock_in_time.strftime('%H:%M')}")

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
        
        await ctx.send(f"{ctx.author.mention} a înregistrat ora de ieșire: {clock_out_time.strftime('%H:%M')} "
                       f"({elapsed_minutes} minute)")

    @clock.command(name="setchannel")
    async def clock_set_channel(self, ctx, event: str, channel: discord.TextChannel):
        """Configurează canalul pentru evenimentul specificat (intrare/ieșire)"""
        if event.lower() not in ["in", "out"]:
            await ctx.send(_("Tipul canalului este invalid. Folosește \"in\" sau \"out\"."))
            return

        event = event.lower()
        data = await self.config.guild(ctx.guild).all()

        if event == "in":
            data["clock_in_channel"] = channel.id
            await ctx.send(_("Canalul pentru evenimentul de intrare a fost configurat."))
        elif event == "out":
            data["clock_out_channel"] = channel.id
            await ctx.send(_("Canalul pentru evenimentul de ieșire a fost configurat."))

        await self.config.guild(ctx.guild).set(data)

    @clock.command(name="resetchannel")
    async def clock_reset_channel(self, ctx, event: str):
        """Resetează canalul pentru evenimentul specificat (intrare/ieșire)"""
        if event.lower() not in ["in", "out"]:
            await ctx.send(_("Tipul canalului este invalid. Folosește \"in\" sau \"out\"."))
            return

        event = event.lower()
        data = await self.config.guild(ctx.guild).all()

        if event == "in":
            data["clock_in_channel"] = None
            await ctx.send(_("Canalul pentru evenimentul de intrare a fost resetat."))
        elif event == "out":
            data["clock_out_channel"] = None
            await ctx.send(_("Canalul pentru evenimentul de ieșire a fost resetat."))

        await self.config.guild(ctx.guild).set(data)
