from .meme import Meme

async def setup(bot):
    await bot.add_cog(Meme(bot))