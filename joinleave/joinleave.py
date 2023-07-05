import discord
from datetime import datetime, timedelta, timezone
from redbot.core import commands, Config
from redbot.core.i18n import Translator, cog_i18n

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
        timestamp = datetime.now(timezone.utc)
        created_at = member.created_at.astimezone(timezone.utc)
        days_since_creation = (timestamp - created_at).days
        user_created = member.created_at.strftime("%Y-%m-%d, %H:%M")
        since_created = days_since_creation
        created_on = f"{user_created} (acum {since_created} zile)"
        embed = discord.Embed(
            description=f"{member.mention} ({member.name}#{member.discriminator})",
            timestamp=member.joined_at,
            color=discord.Color.green())
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_author(name=f"{member.name} a intrat pe serverul de discord", icon_url=member.avatar.url)
        embed.add_field(name="Membri:", value=str(member.guild.member_count), inline=True)
        embed.add_field(name="Cont creeat la:", value=created_on)
        embed.set_footer(text=f"User ID: {member.id}")
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
        timestamp = datetime.now(timezone.utc)
        created_at = member.created_at.astimezone(timezone.utc)
        days_since_creation = (timestamp - created_at).days
        user_created = member.created_at.strftime("%Y-%m-%d, %H:%M")
        since_created = days_since_creation
        created_on = f"{user_created} (acum {since_created} zile)"
        embed = discord.Embed(
            description=f"{member.mention} ({member.name}#{member.discriminator})",
            timestamp=datetime.utcnow(),
            color=discord.Color.red())
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_author(name=f"{member.mention} a părăsit serverul de discord", icon_url=member.avatar.url)
        embed.add_field(name="Membri:", value=str(member.guild.member_count), inline=True)
        embed.add_field(name="Cont creeat la:", value=created_on)
        embed.set_footer(text=f"User ID: {member.id}")
        await channel.send(embed=embed)

    @commands.group()
    async def joinleave(self, ctx):
        """Comenzi pentru evenimentele de intrare/ieșire"""
        pass

    @joinleave.command(name="setchannel")
    async def set_channel(self, ctx, event: str, channel: discord.TextChannel):
        """Configurează canalul pentru evenimentul specificat (intrare/ieșire)"""
        if event.lower() not in ["in", "out"]:
            await ctx.send(_("Tipul canalului este invalid. Folosește \"in\" sau \"out\"."))
            return

        event = event.lower()
        data = await self.config.guild(ctx.guild).all()

        if event == "in":
            data["welcome_channel"] = channel.id
            await ctx.send(_("Canalul pentru evenimentul de intrare a fost configurat."))
        elif event == "out":
            data["farewell_channel"] = channel.id
            await ctx.send(_("Canalul pentru evenimentul de ieșire a fost configurat."))

        await self.config.guild(ctx.guild).set(data)

    @joinleave.command(name="resetchannel")
    async def reset_channel(self, ctx, event: str):
        """Resetează canalul pentru evenimentul specificat (intrare/ieșire)"""
        if event.lower() not in ["in", "out"]:
            await ctx.send(_("Tipul canalului este invalid. Folosește \"in\" sau \"out\"."))
            return

        event = event.lower()
        data = await self.config.guild(ctx.guild).all()

        if event == "in":
            data["welcome_channel"] = None
            await ctx.send(_("Canalul pentru evenimentul de intrare a fost resetat."))
        elif event == "out":
            data["farewell_channel"] = None
            await ctx.send(_("Canalul pentru evenimentul de ieșire a fost resetat."))

        await self.config.guild(ctx.guild).set(data)
