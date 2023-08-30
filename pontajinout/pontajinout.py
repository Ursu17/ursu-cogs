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
            "pontaje": {},  # Dicționar pentru a stoca pontajele individuale
        }
        self.config.register_guild(**default_guild)
        self.bucharest_tz = timezone('Europe/Bucharest')

    # Restul codului on_member_join și on_member_remove

    async def post_message(self, channel, content):
        if channel is not None:
            await channel.send(content)

    def serialize_datetime(self, dt):
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def deserialize_datetime(self, dt_str):
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

    @commands.group()
    async def pontaj(self, ctx):
        """Comenzi pentru înregistrarea pontajului de intrare/ieșire"""
        pass

    @pontaj.command(name="in")
    async def pontaj_in(self, ctx):
        """Înregistrează pontajul de intrare"""
        guild_settings = await self.config.guild(ctx.guild).all()
        user_pontaje = guild_settings["pontaje"].get(ctx.author.id, [])
        user_pontaje.append(self.serialize_datetime(datetime.now(self.bucharest_tz)))
        await self.config.guild(ctx.guild).set_raw("pontaje", ctx.author.id, value=user_pontaje)

        await ctx.message.delete()
        await self.delete_command(ctx)

        guild_settings = await self.config.guild(ctx.guild).all()
        pontaj_in_channel_id = guild_settings["pontaj_in_channel"]
        pontaj_in_channel = ctx.guild.get_channel(pontaj_in_channel_id)

        if pontaj_in_channel:
            await self.post_message(pontaj_in_channel,
                                    f"{ctx.author.mention} a înregistrat pontajul de intrare: {user_pontaje[-1]}")
        else:
            await ctx.send("Canalul pentru înregistrarea pontajului de intrare nu este configurat sau nu există.")

    # Restul codului pentru comenzi și funcții auxiliare

# Instanțiați și adăugați extensia la bot
def setup(bot):
    bot.add_cog(PontajInOut(bot))
