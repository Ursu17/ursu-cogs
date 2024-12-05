from .gameroles import GameRoles

__red_end_user_data_statement__ = 'Acest plugin nu stocheaza date.'

async def setup(bot):
	await bot.add_cog(GameRoles(bot))
