import discord
from redbot.core import commands
from redbot.core import Config
from redbot.core import checks
from redbot.core.utils.chat_formatting import humanize_list
import logging
from typing import Union


class GameRoles(commands.Cog):
	"""Adauga roluri cand un user se joaca un joc."""
	def __init__(self, bot):
		self.bot = bot
		self.log = logging.getLogger('red.flamecogs.gameroles')
		self.cache = {}
		self.config = Config.get_conf(self, identifier=7345167903)
		self.config.register_guild(
			roledict = {},
			doAdd = True,
			doRemove = True
		)

	@commands.guild_only()
	@commands.group(aliases=['gr'])
	async def gameroles(self, ctx):
		"""Comenzi pentru group roles."""
		pass
	
	@checks.guildowner()
	@gameroles.command()
	async def addrole(self, ctx, role: discord.Role):
		"""
		Adauga un grup in lista de group roles.
		
		Rolurile din mai multe cuvinte trebuie adaugate in ghilimele.
		Cel mai mare grad al botului trebuie sa fie fie mai sus decat grupurile pe care le adauga.
		"""
		roledict = await self.config.guild(ctx.guild).roledict()
		rid = str(role.id)
		if rid in roledict:
			return await ctx.send(
				f'`{role.name}` este deja adaugat in lista. '
				f'Foloseste `{ctx.prefix}gameroles addactivity` ca sa adaugi jocul.'
			)
		roledict[role.id] = []
		await self.config.guild(ctx.guild).roledict.set(roledict)
		await ctx.send(
			f'`{role.name}` a fost adaugat in lista! '
			f'Foloseste `{ctx.prefix}gameroles addactivity` ca sa adaugi jocul.'
		)
		if ctx.guild.id in self.cache:
			del self.cache[ctx.guild.id]
	
	@checks.guildowner()
	@gameroles.command()
	async def delrole(self, ctx, role: Union[discord.Role, int]):
		"""
		Scoate un rol din lista.
		
		Rolurile din mai multe cuvinte trebuie adaugate in ghilimele.
		Foloseste id rolului.
		"""
		roledict = await self.config.guild(ctx.guild).roledict()
		if isinstance(role, discord.Role):
			rid = str(role.id)
			name = role.name
		else:
			rid = str(role)
			name = rid
		if rid not in roledict:
			return await ctx.send(f'`{name}` nu este in lista.')
		del roledict[rid]
		await self.config.guild(ctx.guild).roledict.set(roledict)
		await ctx.send(f'`{name}` a fost scos din lista!')
		if ctx.guild.id in self.cache:
			del self.cache[ctx.guild.id]
	
	@checks.guildowner()
	@gameroles.command()
	async def addactivity(self, ctx, role: discord.Role, activity: str):
		"""
		Adauga activitatea ca sa adauge rolul.
		
		Rolurile si activitatile din mai multe cuvinte trebuie adaugate in paranteze.
		Poti primi numele activitatii folosind comanda !ugameroles currentactivity.
		"""
		roledict = await self.config.guild(ctx.guild).roledict()
		rid = str(role.id)
		if rid not in roledict:
			return await ctx.send(f'`{role.name}` nu este in lista de roluri.')
		if activity in roledict[rid]:
			return await ctx.send(f'`{activity}` deja adauga rolul de `{role.name}`.')
		roledict[rid].append(activity)
		await self.config.guild(ctx.guild).roledict.set(roledict)
		await ctx.send(f'`{role.name}` este adaugat automat de `{activity}`!')
		if ctx.guild.id in self.cache:
			del self.cache[ctx.guild.id]
	
	@checks.guildowner()
	@gameroles.command()
	async def delactivity(self, ctx, role: discord.Role, activity: str):
		"""
		Sterge activitatea care adauga rol.
		
		Rolurile si activitatile din mai multe cuvinte trebuie adaugate in paranteze.
		Poti primi numele activitatii folosind comanda !ugameroles currentactivity.
		"""
		roledict = await self.config.guild(ctx.guild).roledict()
		rid = str(role.id)
		if rid not in roledict:
			return await ctx.send(f'`{role.name}` nu este in lista de roluri.')
		if activity not in roledict[rid]:
			return await ctx.send(f'`{activity}` nu adauga rolul de `{role.name}`.')
		roledict[rid].remove(activity)
		await self.config.guild(ctx.guild).roledict.set(roledict)
		await ctx.send(f'`{role.name}` nu va mai fi adaugat de `{activity}`!')
		if ctx.guild.id in self.cache:
			del self.cache[ctx.guild.id]
	
	@checks.guildowner()
	@gameroles.command()
	async def listroles(self, ctx):
		"""Lista de roluri."""
		roledict = await self.config.guild(ctx.guild).roledict()
		rolelist = []
		for rid in roledict:
			role = ctx.guild.get_role(int(rid))
			if role:
				rolelist.append(role.name)
		if rolelist == []:
			return await ctx.send('Nu exista roluri adaugate in lista.')
		roles = '\n'.join(rolelist)
		await ctx.send(
			'Rolurile adaugate:\n'
			f'```\n{roles}```'
		)

	@checks.guildowner()
	@gameroles.command()
	async def listactivities(self, ctx, role: discord.Role):
		"""
		Lista de activitati.
		
		Rolurile cu multe cuvinte trebuie adaugate intre ghilimele.
		"""
		roledict = await self.config.guild(ctx.guild).roledict()
		rid = str(role.id)
		if rid not in roledict:
			return await ctx.send(f'`{role.name}` nu este adaugat in lista.')
		if roledict[rid] == []:
			return await ctx.send(f'`{role.name}` nu are un joc asignat.')
		activities = '\n'.join(roledict[rid])
		await ctx.send(
			f'Activitati care adauga rolul `{role.name}`:\n'
			f'```\n{activities}```'
		)

	@checks.guildowner()
	@gameroles.command()
	async def currentactivity(self, ctx):
		"""Activitatea ta curenta."""
		if not ctx.message.author.activities:
			activity = 'None'
		else:
			activity = '\n'.join(a.name for a in ctx.message.author.activities)
		await ctx.send(f'```\n{activity}```')

	@gameroles.command()
	async def recheck(self, ctx):
		"""Incearca un recheck de activitati."""
		if not ctx.guild.me.guild_permissions.manage_roles:
			return await ctx.send('Nu am permisiunea de manage roles pe server.')
		data = await self.config.guild(ctx.guild).all()
		roledict = data['roledict']
		doAdd = data['doAdd']
		doRemove = data['doRemove']
		torem = set()
		toadd = set()
		failed = set()
		for role in ctx.author.roles:
			if str(role.id) in roledict:
				if ctx.guild.me.top_role > role:
					torem.add(role)
				else:
					failed.add(role) 
		activities = [a.name for a in ctx.author.activities]
		for role in [rid for rid in roledict if any(a in roledict[rid] for a in activities)]:
			role = ctx.guild.get_role(int(role))
			if role is not None and ctx.guild.me.top_role > role:
				toadd.add(role)
			elif role:
				failed.add(role)
		setsum = torem & toadd
		torem -= setsum
		toadd -= setsum
		#Filter out managed roles like Nitro Booster
		torem = [r for r in torem if not r.managed]
		toadd = [r for r in toadd if not r.managed]
		if toadd and doAdd:
			try:
				await ctx.author.add_roles(*toadd, reason='Gameroles')
			except discord.errors.Forbidden:
				return await ctx.send(
					'Encountered an unexpected discord.errors.Forbidden adding roles, canceling'
				)
		if torem and doRemove:
			try:
				await ctx.author.remove_roles(*torem, reason='Gameroles')
			except discord.errors.Forbidden:
				return await ctx.send(
					'Encountered an unexpected discord.errors.Forbidden removing roles, canceling'
				)
		if failed:
			await ctx.send(
				'The following roles could not be managed '
				f'because they are higher than my highest role:\n`{humanize_list(list(failed))}`'
			)
		await ctx.tick()

	@commands.guild_only()
	@checks.guildowner()
	@commands.group(aliases=['grset'], invoke_without_command=True)
	async def gameroleset(self, ctx):
		"""Configureaza plugin."""
		await ctx.send_help()
		data = await self.config.guild(ctx.guild).all()
		msg = (
			'Adauga roluri: {doAdd}\n'
			'Sterge roluri: {doRemove}\n'
		).format_map(data)
		await ctx.send(f'```py\n{msg}```')
		
	@gameroleset.command()
	async def add(self, ctx, value: bool=None):
		"""
		Seteaza daca adaug rolurile cand cineva se joaca.
		
		Defaults este true.
		Valoarea este server specific.
		"""
		if value is None:
			v = await self.config.guild(ctx.guild).doAdd()
			if v:
				await ctx.send('Rolurile sunt adaugate cand cineva incepe sa joace.')
			else:
				await ctx.send('Rolurile nu sunt adaugate cand cienva incepe sa joace.')
		else:
			await self.config.guild(ctx.guild).doAdd.set(value)
			if value:
				await ctx.send('Rolurile vor fi adaugate de acum cand cineva incepe sa joace.')
			else:
				await ctx.send('Rolurile nu vor mai va fi adaugate de acum cand cineva incepe sa joace.')
			if ctx.guild.id in self.cache:
				del self.cache[ctx.guild.id]
		
	@gameroleset.command()
	async def remove(self, ctx, value: bool=None):
		"""
		Set if roles should be removed when someone stops playing a game.
		
		Defaults to True.
		This value is server specific.
		"""
		if value is None:
			v = await self.config.guild(ctx.guild).doRemove()
			if v:
				await ctx.send('Rolurile vor fi sterse cand cineva nu se mai joaca.')
			else:
				await ctx.send('Rolurile nu vor mai fi sterse cand cineva nu se mai joaca.')
		else:
			await self.config.guild(ctx.guild).doRemove.set(value)
			if value:
				await ctx.send('Rolurile vor fi sterse de acum cand cineva nu se mai joaca.')
			else:
				await ctx.send('Rolurile nu vor mai fi sterse cand cineva nu se mai joaca.')
			if ctx.guild.id in self.cache:
				del self.cache[ctx.guild.id]

	async def red_delete_data_for_user(self, **kwargs):
		"""Nimic de sters."""
		return
				
	@commands.Cog.listener()
	async def on_member_update(self, beforeMem, afterMem):
		"""Actualizeaza rolurile unei persoane dpy 1.7"""
		if discord.version_info.major == 1:
			await self.update_gameroles(beforeMem, afterMem)
	
	@commands.Cog.listener()
	async def on_presence_update(self, beforeMem, afterMem):
		"""Actualizeaza rolurile unei persoane dpy 2.0"""
		# This should never be run on dpy 1.7, but just in case I don't want to try to apply the same change twice.
		if discord.version_info.major == 2:
			await self.update_gameroles(beforeMem, afterMem)
		
	async def update_gameroles(self, beforeMem, afterMem):
		"""Update a member's roles."""
		if beforeMem.activities == afterMem.activities:
			return
		if await self.bot.cog_disabled_in_guild(self, afterMem.guild):
			return
		if afterMem.guild.id not in self.cache:
			data = await self.config.guild(afterMem.guild).all()
			self.cache[afterMem.guild.id] = data
		roledict = self.cache[afterMem.guild.id]['roledict']
		if not roledict:
			return
		doAdd = self.cache[afterMem.guild.id]['doAdd']
		doRemove = self.cache[afterMem.guild.id]['doRemove']
		if not (doAdd or doRemove):
			return
		torem = set()
		toadd = set()
		#REMOVE
		for role_obj in afterMem.roles:
			if str(role_obj.id) in roledict:
				if afterMem.guild.me.top_role > role_obj:
					torem.add(role_obj)
				else:
					self.log.warning(
						f'Rol {role_obj} ({role_obj.id}) din server '
						f'{afterMem.guild} ({afterMem.guild.id}) este mai mare decat cel mai mare rol al meu.'
					)
		#ADD
		activities = [a.name for a in afterMem.activities]
		for role in [rid for rid in roledict if any(a in roledict[rid] for a in activities)]:
			role_obj = afterMem.guild.get_role(int(role))
			if role_obj is not None and afterMem.guild.me.top_role > role_obj:
				toadd.add(role_obj)
			elif role_obj:
				self.log.warning(
					f'Rolul {role_obj} ({role}) din serverul '
					f'{afterMem.guild} ({afterMem.guild.id}) este mai mare decat cel mai mare rol al meu.'
				)
			else:
				self.log.warning(
					f'Rolul {role} din serverul {afterMem.guild} ({afterMem.guild.id}) '
					's-ar putea sa nu mai existe.'
				)
		setsum = torem & toadd
		torem -= setsum
		toadd -= setsum
		if not (torem or toadd):
			return
		if not afterMem.guild.me.guild_permissions.manage_roles:
			self.log.debug(
				f'Nu am permisiunea de manage roles pe {afterMem.guild} ({afterMem.guild.id}).'
			)
			return
		#Filter out managed roles like Nitro Booster
		torem = [r for r in torem if not r.managed]
		toadd = [r for r in toadd if not r.managed]
		if torem and doRemove:
			try:
				await afterMem.remove_roles(*torem, reason='Gameroles')
			except discord.errors.Forbidden:
				self.log.exception(
					'Encountered an unexpected discord.errors.Forbidden removing roles '
					f'from {afterMem} in {afterMem.guild} ({afterMem.guild.id}).'
				)
		if toadd and doAdd:
			try:
				await afterMem.add_roles(*toadd, reason='Gameroles')
			except discord.errors.Forbidden:
				self.log.exception(
					'Encountered an unexpected discord.errors.Forbidden adding roles '
					f'to {afterMem} in {afterMem.guild} ({afterMem.guild.id}).'
				)
