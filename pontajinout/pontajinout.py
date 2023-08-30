import discord
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
        default_user = {
            "in": None,
            "out": None
        }
        self.config.register_user(**default_user)
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
        user_pontaje = await self.config.user(ctx.author).all()
        if user_pontaje["in"] is not None:
            await ctx.send("Ai înregistrat deja un pontaj 'in'.")
            return

        user_pontaje["in"] = datetime.now(self.bucharest_tz).strftime('%H:%M')
        await self.config.user(ctx.author).set(user_pontaje)
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention} a intrat în tură la ora {user_pontaje['in']}")

    @pontaj.command(name="out")
    async def pontaj_out(self, ctx):
        """Înregistrează pontajul de ieșire și calculează durata de lucru"""
        user_pontaje = await self.config.user(ctx.author).all()
        if user_pontaje["in"] is None:
            await ctx.send("Folosește mai întâi **!pontaj in**.")
            return

        if user_pontaje["out"] is not None:
            await ctx.send("Ai înregistrat deja un pontaj 'out'.")
            return

        user_pontaje["out"] = datetime.now(self.bucharest_tz).strftime('%H:%M')
        await self.config.user(ctx.author).set(user_pontaje)
        await ctx.message.delete()

        in_time = datetime.strptime(user_pontaje["in"], '%H:%M')
        out_time = datetime.strptime(user_pontaje["out"], '%H:%M')
        work_duration = out_time - in_time
        work_minutes = int(work_duration.total_seconds() / 60)

        await ctx.send(f"{ctx.author.mention} a ieșit din tură la ora {user_pontaje['out']} "
                       f"(A stat în tură {work_minutes} de minute)")

# Instanțiați și adăugați extensia la bot
def setup(bot):
    bot.add_cog(PontajInOut(bot))
