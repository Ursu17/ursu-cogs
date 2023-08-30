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
        default_guild = {
            "pontaj_in_channel": None,
            "pontaj_out_channel": None,
        }
        self.config.register_guild(**default_guild)
        self.pontaj_in_time = None
        self.bucharest_tz = timezone('Europe/Bucharest')

    # Restul codului on_member_join și on_member_remove

    async def post_message(self, channel, content):
        if channel is not None:
            await channel.send(content)

    # Restul codului pentru comenzi

    @pontaj.command(name="in")
    async def pontaj_in(self, ctx):
        """Înregistrează pontajul de intrare"""
        self.pontaj_in_time = datetime.now(self.bucharest_tz)
        await ctx.message.delete()
        await self.delete_command(ctx)

        guild_settings = await self.config.guild(ctx.guild).all()
        pontaj_in_channel_id = guild_settings["pontaj_in_channel"]
        pontaj_in_channel = ctx.guild.get_channel(pontaj_in_channel_id)

        if pontaj_in_channel:
            await self.post_message(pontaj_in_channel,
                                    f"{ctx.author.mention} a înregistrat pontajul de intrare: {self.pontaj_in_time.strftime('%H:%M')}")
        else:
            await ctx.send("Canalul pentru înregistrarea pontajului de intrare nu este configurat sau nu există.")

    @pontaj.command(name="out")
    async def pontaj_out(self, ctx):
        """Înregistrează pontajul de ieșire și calculează durata de lucru"""
        if not hasattr(self, "pontaj_in_time") or self.pontaj_in_time is None:
            await ctx.message.delete()
            return
        
        pontaj_out_time = datetime.now(self.bucharest_tz)
        work_duration = pontaj_out_time - self.pontaj_in_time
        work_minutes = int(work_duration.total_seconds() / 60)
        self.pontaj_in_time = None
        
        await ctx.message.delete()
        await self.delete_command(ctx)
        
        guild_settings = await self.config.guild(ctx.guild).all()
        pontaj_out_channel_id = guild_settings["pontaj_out_channel"]
        pontaj_out_channel = ctx.guild.get_channel(pontaj_out_channel_id)

        if pontaj_out_channel:
            await self.post_message(pontaj_out_channel,
                                    f"{ctx.author.mention} a înregistrat pontajul de ieșire: {pontaj_out_time.strftime('%H:%M')} "
                                    f"({work_minutes} minute)")
        else:
            await ctx.send("Canalul pentru înregistrarea pontajului de ieșire nu este configurat sau nu există.")

    # Restul codului pentru comenzi

    async def delete_command(self, ctx):
        await ctx.message.delete(delay=3)  # Șterge mesajul după 3 secunde

# Instanțiați și adăugați extensia la bot
def setup(bot):
    bot.add_cog(PontajInOut(bot))
