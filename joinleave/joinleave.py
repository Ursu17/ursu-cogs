import discord
from datetime import datetime
from redbot.core import commands, Config
from redbot.core.i18n import Translator

_ = Translator("JoinLeave", __file__)


class JoinLeave(commands.Cog):
    """Cog pentru gestionarea evenimentelor de intrare și ieșire."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Schimbă identifier-ul cu unul unic
        default_guild = {
            "welcome_channel": None,
            "farewell_channel": None,
        }
        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel_id = await self.config.guild(member.guild).welcome_channel()
        if welcome_channel_id:
            welcome_channel = member.guild.get_channel(welcome_channel_id)
            if welcome_channel:
                embed = discord.Embed(
                    title=_("Bun venit!"),
                    description=f"{member.mention} a intrat pe serverul nostru!",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow(),
                )
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                await welcome_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        farewell_channel_id = await self.config.guild(member.guild).farewell_channel()
        if farewell_channel_id:
            farewell_channel = member.guild.get_channel(farewell_channel_id)
            if farewell_channel:
                embed = discord.Embed(
                    title=_("Rămas bun!"),
                    description=f"{member.name} a părăsit serverul nostru!",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                )
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                await farewell_channel.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    async def setchannel(self, ctx, action: str, channel: discord.TextChannel):
        """Setează canalul pentru evenimentele de intrare și ieșire."""
        if action.lower() not in ["in", "out"]:
            await ctx.send(_("Tipul canalului este invalid. Folosește 'in' sau 'out'."))
            return

        if action.lower() == "in":
            await self.config.guild(ctx.guild).welcome_channel.set(channel.id)
            await ctx.send(_("Canalul de bun venit a fost setat la {channel}").format(channel=channel.mention))
        elif action.lower() == "out":
            await self.config.guild(ctx.guild).farewell_channel.set(channel.id)
            await ctx.send(_("Canalul de rămas bun a fost setat la {channel}").format(channel=channel.mention))

    async def red_delete_data_for_user(self, **kwargs):
        """Nu stochează date despre utilizatori."""
        return
