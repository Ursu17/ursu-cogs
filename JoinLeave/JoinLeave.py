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
        pass  # This cog stores no EUD

    def __init__(self):
        self.config = Config.get_conf(self, identifier=17101996)
        default_guild_settings = {
            "channel_bun_venit": None,
            "channel_ramas_bun": None,
        }
        self.config.register_guild(**default_guild_settings)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel_id = await self.config.guild(guild).channel_bun_venit()
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title=_("Bun venit pe server!"),
                    description=_("Legiunea EU a intrat pe serverul de Discord al guildului respectiv!"),
                    color=discord.Color.green(),
                )
                embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name=_("Legiunea EU"), value=f"{member.name}#{member.discriminator}")
                embed.set_footer(text=_("Număr total de membri: {count} | Legiunea Guild - Since Jul 2023").format(count=guild.member_count))
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        channel_id = await self.config.guild(guild).channel_ramas_bun()
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title=_("La revedere!"),
                    description=_("Legiunea EU a ieșit de pe serverul de Discord al guildului respectiv. Sperăm să vă mai întoarceți pe server!"),
                    color=discord.Color.red(),
                )
                embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name=_("Legiunea EU plecată"), value=f"{member.name}#{member.discriminator}")
                embed.set_footer(text=_("Număr total de membri: {count} | Legiunea Guild - Since Jul 2023").format(count=guild.member_count))
                await channel.send(embed=embed)

    @commands.group(name="joinleave")
    async def joinleave(self, ctx):
        """Comenzi pentru setarea canalului de Join și Leave"""
        pass

    @joinleave.command(name="setchannel")
    @commands.has_permissions(manage_guild=True)
    async def set_channel(self, ctx, event_type: str, channel: discord.TextChannel):
        """Setează canalul pentru mesajul de bun venit sau rămas bun"""
        guild = ctx.guild
        event_type = event_type.lower()
        if event_type == "bun_venit":
            await self.config.guild(guild).channel_bun_venit.set(channel.id)
            await ctx.send(_("Canalul pentru mesajul de bun venit a fost setat la {channel}.").format(channel=channel.mention))
        elif event_type == "ramas_bun":
            await self.config.guild(guild).channel_ramas_bun.set(channel.id)
            await ctx.send(_("Canalul pentru mesajul de rămas bun a fost setat la {channel}.").format(channel=channel.mention))
        else:
            await ctx.send(_("Te rog specifică un tip valid: `bun_venit` sau `ramas_bun`."))


def setup(bot):
    bot.add_cog(JoinLeave(bot))
