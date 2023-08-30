import discord
from datetime import datetime, timezone
from redbot.core import commands, Config
from redbot.core.i18n import Translator, cog_i18n

_ = Translator("ClockInOut", __file__)

@cog_i18n(_)
class ClockInOut(commands.Cog):
    """Pontaj In/Out events"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "pontaj_in_channel": None,
            "pontaj_out_channel": None,
        }
        self.config.register_guild(**default_guild)
        self.pontaj_in_time = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await self.config.guild(member.guild).all()
        # Restul codului on_member_join

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = await self.config.guild(member.guild).all()
        # Restul codului on_member_remove

    @commands.group()
    async def pontaj(self, ctx):
        """Comenzi pentru înregistrarea pontajului de intrare/ieșire"""
        pass

    @pontaj.command(name="in")
    async def pontaj_in(self, ctx):
        """Înregistrează pontajul de intrare"""
        self.pontaj_in_time = datetime.now(timezone.utc)
        await ctx.send(f"{ctx.author.mention} a înregistrat pontajul de intrare: {self.pontaj_in_time.strftime('%H:%M')}")

    @pontaj.command(name="out")
    async def pontaj_out(self, ctx):
        """Înregistrează pontajul de ieșire și calculează durata de lucru"""
        if not hasattr(self, "pontaj_in_time") or self.pontaj_in_time is None:
            await ctx.send("Nu ai înregistrat încă pontajul de intrare.")
            return
        
        pontaj_out_time = datetime.now(timezone.utc)
        work_duration = pontaj_out_time - self.pontaj_in_time
        work_minutes = int(work_duration.total_seconds() / 60)
        self.pontaj_in_time = None
        
        await ctx.send(f"{ctx.author.mention} a înregistrat pontajul de ieșire: {pontaj_out_time.strftime('%H:%M')} "
                       f"({work_minutes} minute)")

    @pontaj.command(name="setchannel")
    async def pontaj_set_channel(self, ctx, event: str, channel: discord.TextChannel):
        """Configurează canalul pentru evenimentul specificat (intrare/ieșire)"""
        if event.lower() not in ["in", "out"]:
            await ctx.send(_("Tipul canalului este invalid. Folosește \"in\" sau \"out\"."))
            return

        event = event.lower()
        data = await self.config.guild(ctx.guild).all()

        if event == "in":
            data["pontaj_in_channel"] = channel.id
            await ctx.send(_("Canalul pentru evenimentul de intrare a fost configurat."))
        elif event == "out":
            data["pontaj_out_channel"] = channel.id
            await ctx.send(_("Canalul pentru evenimentul de ieșire a fost configurat."))

        await self.config.guild(ctx.guild).set(data)

    @pontaj.command(name="resetchannel")
    async def pontaj_reset_channel(self, ctx, event: str):
        """Resetează canalul pentru evenimentul specificat (intrare/ieșire)"""
        if event.lower() not in ["in", "out"]:
            await ctx.send(_("Tipul canalului este invalid. Folosește \"in\" sau \"out\"."))
            return

        event = event.lower()
        data = await self.config.guild(ctx.guild).all()

        if event == "in":
            data["pontaj_in_channel"] = None
            await ctx.send(_("Canalul pentru evenimentul de intrare a fost resetat."))
        elif event == "out":
            data["pontaj_out_channel"] = None
            await ctx.send(_("Canalul pentru evenimentul de ieșire a fost resetat."))

        await self.config.guild(ctx.guild).set(data)
