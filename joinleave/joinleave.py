import discord
import datetime
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
            "channel": None,
            "join": True,
            "leave": True
        }
        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        join = await self.config.guild(member.guild).join()
        if not join:
            return
        channel = member.guild.get_channel(
            await self.config.guild(member.guild).channel()
        )
        if not channel:
            return
        time = datetime.datetime.utcnow()
        users = len(member.guild.members)
        since_created = (time - member.created_at).days
        user_created = member.created_at.strftime("%Y-%m-%d, %H:%M")
        created_on = f"{user_created} ({since_created} days ago)"

        embed = discord.Embed(
            description=f"{member.mention} ({member.name}#{member.discriminator})",
            colour=discord.Colour.green(),
            timestamp=member.joined_at,
        )
        embed.add_field(name="Total Membrii:", value=str(users))
        embed.add_field(name="Cont creeat la:", value=created_on)
        embed.set_footer(text=f"User ID: {member.id}")
        embed.set_author(
            name=f"{member.name} a intrat pe serverul de discord",
            url=member.avatar_url,
            icon_url=member.avatar_url,
        )
        embed.set_thumbnail(url=member.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        leave = await self.config.guild(member.guild).leave()
        if not leave:
            return
        channel = member.guild.get_channel(
            await self.config.guild(member.guild).channel()
        )
        if not channel:
            return
        time = datetime.datetime.utcnow()
        users = len(member.guild.members)

        embed = discord.Embed(
            description=f"{member.mention} ({member.name}#{member.discriminator})",
            colour=discord.Colour.red(),
            timestamp=time,
        )
        embed.add_field(name="Total Membrii:", value=str(users))
        embed.set_footer(text=f"User ID: {member.id}")
        embed.set_author(
            name=f"{member.name} a iesit de pe serverul de discord",
            url=member.avatar_url,
            icon_url=member.avatar_url,
        )
        embed.set_thumbnail(url=member.avatar_url)
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
