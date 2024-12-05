import discord
from redbot.core import commands
import aiohttp

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_meme(self):
        url = 'https://meme-api.com/gimme'
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(url) as response:
                    data = await response.json()
                    if not data.get('nsfw', False):  # Check if the meme is not NSFW
                        return data

    @commands.command()
    async def meme(self, ctx):
        """Posteaza un meme non porn."""
        meme_data = await self.fetch_meme()

        author = meme_data['author']
        title = meme_data['title']
        post_link = meme_data['postLink']
        meme_url = meme_data['url']

        embed = discord.Embed(title=title, color=await ctx.embed_color())
        embed.set_author(name=author)
        embed.add_field(name="Post Link", value=post_link, inline=False)
        embed.set_image(url=meme_url)

        await ctx.send(embed=embed)