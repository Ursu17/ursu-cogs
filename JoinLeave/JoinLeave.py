import discord
from redbot.core import commands, Config

class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=17101996)  # Cod de identificare actualizat

        default_guild_settings = {
            "channel_bun_venit": None,
            "channel_ramas_bun": None
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
                    title="Bun venit pe server!",
                    description=f"Legiunea EU a intrat pe serverul de Discord al guildului respectiv!",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name="Legiunea EU", value=f"{member.name}#{member.discriminator}")
                embed.set_footer(text=f"Număr total de membri: {guild.member_count} | Legiunea Guild - Since Jul 2023")
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        channel_id = await self.config.guild(guild).channel_ramas_bun()
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="La revedere!",
                    description=f"Legiunea EU a ieșit de pe serverul de Discord al guildului respectiv. Sperăm să vă mai întoarceți pe server!",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name="Legiunea EU plecată", value=f"{member.name}#{member.discriminator}")
                embed.set_footer(text=f"Număr total de membri: {guild.member_count} | Legiunea Guild - Since Jul 2023")
                await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setchannel(self, ctx, event_type: str, channel: discord.TextChannel):
        guild = ctx.guild
        event_type = event_type.lower()
        if event_type == "bun_venit":
            await self.config.guild(guild).channel_bun_venit.set(channel.id)
            await ctx.send(f"Canalul pentru mesajul de bun venit a fost setat la {channel.mention}.")
        elif event_type == "ramas_bun":
            await self.config.guild(guild).channel_ramas_bun.set(channel.id)
            await ctx.send(f"Canalul pentru mesajul de rămas bun a fost setat la {channel.mention}.")
        else:
            await ctx.send("Te rog specifică un tip valid: `bun_venit` sau `ramas_bun`.")

def setup(bot):
    bot.add_cog(JoinLeave(bot))
