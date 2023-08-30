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
            "pontaje": {},  # Dicționar pentru a stoca pontajele individuale
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
        user_pontaje.append(self.bucharest_tz.localize(datetime.now()))
        await self.config.guild(ctx.guild).set_raw("pontaje", ctx.author.id, value=[dt.isoformat() for dt in user_pontaje])

        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass

        guild_settings = await self.config.guild(ctx.guild).all()
        pontaj_in_channel_id = guild_settings["pontaj_in_channel"]
        pontaj_in_channel = ctx.guild.get_channel(pontaj_in_channel_id)

        if pontaj_in_channel:
            await self.post_message(pontaj_in_channel,
                                    f"{ctx.author.mention} a înregistrat pontajul de intrare la ora {user_pontaje[-1].strftime('%H:%M')}")
        else:
            await ctx.send("Canalul pentru înregistrarea pontajului de intrare nu este configurat sau nu există.")

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

        if user_pontaje:
            pontaj_out_time = self.bucharest_tz.localize(datetime.now())
            work_duration = pontaj_out_time - user_pontaje[-1]
            work_minutes = int(work_duration.total_seconds() / 60)

            await ctx.send(f"{ctx.author.mention} a ieșit din tură la ora {pontaj_out_time.strftime('%H:%M')} "
                           f"(A stat în tură {work_minutes} minute)")

            await self.config.guild(ctx.guild).set_raw("pontaje", ctx.author.id, value=user_pontaje[:-1])

            try:
                await ctx.message.delete()
            except discord.NotFound:
                pass

            guild_settings = await self.config.guild(ctx.guild).all()
            pontaj_out_channel_id = guild_settings["pontaj_out_channel"]
            pontaj_out_channel = ctx.guild.get_channel(pontaj_out_channel_id)

            if pontaj_out_channel:
                await self.post_message(pontaj_out_channel,
                                        f"{ctx.author.mention} a ieșit din tură la ora {pontaj_out_time.strftime('%H:%M')} "
                                        f"(A stat în tură {work_minutes} minute)")
            else:
                await ctx.send("Canalul pentru înregistrarea pontajului de ieșire nu este configurat sau nu există.")

            await asyncio.sleep(3)
            try:
                await ctx.message.delete()
            except discord.NotFound:
                pass
        else:
            await ctx.send("Folosește mai întâi **!pontaj in**.")

# Instanțiați și adăugați extensia la bot
def setup(bot):
    bot.add_cog(PontajInOut(bot))
