from redbot.core import commands, Config
from redbot.core.i18n import Translator, cog_i18n
import discord
import datetime

_ = Translator("JoinLeave", __file__)

@cog_i18n(_)
class JoinLeave(commands.Cog):
    """Join/Leave events"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "welcome_channel": None,
            "farewell_channel": None,
        }
        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await self.config.guild(member.guild).all()
        channel_id = data["welcome_channel"]
        if channel_id is None:
            return
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return
        timestamp = datetime.datetime.utcnow()
        embed = discord.Embed(color=discord.Color.green())
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=f"{member.name} a intrat pe serverul de Discord", icon_url=member.avatar_url)
        embed.add_field(name="Membri:", value=str(member.guild.member_count), inline=True)
        embed.set_footer(text=f"Data și ora: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = await self.config.guild(member.guild).all()
        channel_id = data["farewell_channel"]
        if channel_id is None:
            return
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return
        timestamp = datetime.datetime.utcnow()
        embed = discord.Embed(color=discord.Color.red())
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=f"{member.name} a părăsit serverul de Discord", icon_url=member.avatar_url)
        embed.add_field(name="Membri:", value=str(member.guild.member_count), inline=True)
        embed.set_footer(text=f"Data și ora: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        await channel.send(embed=embed)

    @commands.group()
    async def joinleave(self, ctx):
        """Comenzi pentru evenimentele de intrare/ieșire"""
        pass

    @joinleave.command(name="setchannel")
    async def set_channel(self, ctx, event: str, channel: discord.TextChannel):
        """Configurează canalul pentru evenimentul specificat (intrare/ieșire)"""
        if event.lower() not in ["intrare", "ieșire"]:
            await ctx.send(_("Tipul canalului este invalid. Folosește \"intrare\" sau \"ieșire\"."))
            return

        event = event.lower()
        data = await self.config.guild(ctx.guild).all()

        if event == "intrare":
            data["welcome_channel"] = channel.id
            await ctx.send(_("Canalul pentru evenimentul de intrare a fost configurat."))
        elif event == "ieșire":
            data["farewell_channel"] = channel.id
            await ctx.send(_("Canalul pentru evenimentul de ieșire a fost configurat."))

        await self.config.guild(ctx.guild).set(data)

    @joinleave.command(name="resetchannel")
    async def reset_channel(self, ctx, event: str):
        """Resetează canalul pentru evenimentul specificat (intrare/ieșire)"""
        if event.lower() not in ["intrare", "ieșire"]:
            await ctx.send(_("Tipul canalului este invalid. Folosește \"intrare\" sau \"ieșire\"."))
            return

        event = event.lower()
        data = await self.config.guild(ctx.guild).all()

        if event == "intrare":
            data["welcome_channel"] = None
            await ctx.send(_("Canalul pentru evenimentul de intrare a fost resetat."))
        elif event == "ieșire":
            data["farewell_channel"] = None
            await ctx.send(_("Canalul pentru evenimentul de ieșire a fost resetat."))

        await self.config.guild(ctx.guild).set(data)
