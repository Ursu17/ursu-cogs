from redbot.core import commands, Config
from redbot.core.i18n import Translator, cog_i18n
import discord

_ = Translator("AutoRoler", __file__)


@cog_i18n(_)
class AutoRoler(commands.Cog):
    """AutoRoler"""

    __version__ = "2.0.0"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nVersiunea: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        pass  # This cog stores no EUD

    def __init__(self):
        self.config = Config.get_conf(self, identifier=300920211119)
        default_guild = {
            "enabled": False,
            "roles": [],
        }
        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await self.config.guild(member.guild).all()
        if not data["enabled"]:
            return
        await member.add_roles(*[member.guild.get_role(role_id) for role_id in data["roles"]])

    @commands.group()
    async def autorole(self, ctx):
        """Comenzi roluri"""
        pass

    @autorole.command()
    async def add(self, ctx, role: discord.Role):
        """Adauga un rol pentru cei care intra pe server"""
        async with self.config.guild(ctx.guild).roles() as roles:
            if role.id in roles:
                await ctx.send(_("Rolul este deja asignat"))
                return
            roles.append(role.id)
            await ctx.send(_("{} a fost asignat").format(role.mention))

    @autorole.command()
    async def remove(self, ctx, role: discord.Role):
        """Sterge un rol din lista de asignare"""
        async with self.config.guild(ctx.guild).roles() as roles:
            if role.id not in roles:
                await ctx.send(_("Rolul nu este asignat"))
                return
            roles.remove(role.id)
            await ctx.send(_("{} a fost scos din lista de asignare").format(role.mention))

    @autorole.command()
    async def list(self, ctx):
        """O lista cu rolurile de asignare"""
        async with self.config.guild(ctx.guild).roles() as roles:
            if not roles:
                await ctx.send(_("Nu exista roluri in lista de asignare"))
                return
            role_mentions = [ctx.guild.get_role(role_id).mention for role_id in roles]
            await ctx.send(_("Lista rolurilor: {}").format(", ".join(role_mentions)))

    @autorole.command()
    async def enable(self, ctx):
        """Porneste autorolurile"""
        await self.config.guild(ctx.guild).enabled.set(True)
        await ctx.send(_("AutoRoler pornit"))

    @autorole.command()
    async def disable(self, ctx):
        """Opreste autorolurile"""
        await self.config.guild(ctx.guild).enabled.set(False)
        await ctx.send(_("AutoRoler oprit"))
