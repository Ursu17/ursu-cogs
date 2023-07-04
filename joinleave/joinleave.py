from redbot.core import commands, Config
from redbot.core.i18n import Translator, cog_i18n
import discord

_ = Translator("JoinLeave", __file__)


@cog_i18n(_)
class JoinLeave(commands.Cog):
    """JoinLeave"""

    __version__ = "1.0.0"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nVersion: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        pass

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=300920211119)
        default_guild = {
            "welcome_channel": None,
            "farewell_channel": None,
            "welcome_message": "Bun venit, {member.mention}! Bine ai venit pe server!",
            "farewell_message": "La revedere, {member.name}! Te mai așteptăm pe server!",
        }
        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await self.config.guild(member.guild).all()
        welcome_channel_id = data["welcome_channel"]
        welcome_message = data["welcome_message"]
        welcome_channel = self.bot.get_channel(welcome_channel_id)
        if welcome_channel is not None and welcome_message:
            message = welcome_message.format(member=member)
            await welcome_channel.send(message)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = await self.config.guild(member.guild).all()
        farewell_channel_id = data["farewell_channel"]
        farewell_message = data["farewell_message"]
        farewell_channel = self.bot.get_channel(farewell_channel_id)
        if farewell_channel is not None and farewell_message:
            message = farewell_message.format(member=member)
            await farewell_channel.send(message)

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.group()
    async def joinleave(self, ctx):
        """Comenzi pentru canalul de bun venit și rămas bun."""
        pass

    @joinleave.command(name="setchannel")
    async def set_channel(self, ctx, channel_type: str, channel: discord.TextChannel):
        """Setează canalul de bun venit sau rămas bun."""
        if channel_type.lower() == "welcome":
            await self.config.guild(ctx.guild).welcome_channel.set(channel.id)
            await ctx.send(_("Canalul de bun venit a fost setat."))
        elif channel_type.lower() == "farewell":
            await self.config.guild(ctx.guild).farewell_channel.set(channel.id)
            await ctx.send(_("Canalul de rămas bun a fost setat."))
        else:
            await ctx.send(_("Tipul canalului este invalid. Folosește \"welcome\" sau \"farewell\"."))

    @joinleave.command(name="setmessage")
    async def set_message(self, ctx, message_type: str, *, message: str):
        """Setează mesajul de bun venit sau rămas bun."""
        if message_type.lower() == "welcome":
            await self.config.guild(ctx.guild).welcome_message.set(message)
            await ctx.send(_("Mesajul de bun venit a fost setat."))
        elif message_type.lower() == "farewell":
            await self.config.guild(ctx.guild).farewell_message.set(message)
            await ctx.send(_("Mesajul de rămas bun a fost setat."))
        else:
            await ctx.send(_("Tipul mesajului este invalid. Folosește \"welcome\" sau \"farewell\"."))


async def setup(bot):
    cog = JoinLeave(bot)
    await cog.initialize()
    bot.add_cog(cog)
