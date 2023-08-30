import discord
import asyncio
from datetime import datetime
from redbot.core import commands, Config
from redbot.core.i18n import Translator, cog_i18n
from pytz import timezone

_ = Translator("PontajInOut", __file__)

@cog_i18n(_)
class PontajInOut(commands.Cog):
    """Pontaj In/Out events"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "pontaj_in_channel": None,
            "pontaj_out_channel": None,
            "pontaje": {},  # Dicționar pentru a stoca pontaje individuale pentru fiecare utilizator
        }
        self.config.register_guild(**default_guild)
        self.bucharest_tz = timezone('Europe/Bucharest')

    async def post_message(self, channel, content):
        if channel is not None:
            await channel.send(content)

    @commands.group()
    async def pontaj(self, ctx):
        """Comenzi pentru înregistrarea pontajului de intrare/ieșire"""
        pass

    @pontaj.command(name="in")
    async def pontaj_in(self, ctx):
        """Înregistrează pontajul de intrare"""
        guild_settings = await self.config.guild(ctx.guild).all()
        user_pontaje = guild_settings["pontaje"].get(ctx.author.id, [])
        user_pontaje.append(datetime.now(self.bucharest_tz))
        await self.config.guild(ctx.guild).set_raw("pontaje", ctx.author.id, value=[dt.isoformat() for dt in user_pontaje])

        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass

        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass

    @pontaj.command(name="out")
    async def pontaj_out(self, ctx):
        """Înregistrează pontajul de ieșire și calculează durata de lucru"""
        guild_settings = await self.config.guild(ctx.guild).all()
        user_pontaje = guild_settings["pontaje"].get(ctx.author.id, [])

        if not user_pontaje:
            await ctx.send("Folosește mai întâi **!pontaj in**.")
            return
        
        pontaj_out_time = datetime.now(self.bucharest_tz)
        work_duration = pontaj_out_time - user_pontaje[-1]
        work_minutes = int(work_duration.total_seconds() / 60)
        user_pontaje.pop()  # Scoatem ultimul pontaj de intrare

        await self.config.guild(ctx.guild).set_raw("pontaje", ctx.author.id, value=[dt.isoformat() for dt in user_pontaje])

        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass

        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass

        await ctx.send(f"Clock in: {user_pontaje[-1].strftime('%H:%M')} | Clock Out: {pontaj_out_time.strftime('%H:%M')} "
                       f"({work_minutes} minute)")

    # Restul codului pentru comenzi și funcții auxiliare

# Instanțiați și adăugați extensia la bot
def setup(bot):
    bot.add_cog(PontajInOut(bot))
