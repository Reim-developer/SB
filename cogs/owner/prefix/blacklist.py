from typing import Optional
from discord import TextChannel, User, Embed
from discord.ext import commands
from core_utils.container import container_instance
from sql.blacklist_manager import BlacklistManager, BlacklistResult
from datetime import datetime
from json_helper import prefix

class BlackListPrefix(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

		self.__pool = container_instance.get_postgres_manager().pool
		assert self.__pool is not None
		self.__blacklist_manager = BlacklistManager(self.__pool)
		self.LOG_CHANNEL = self.bot.get_channel(1057274847459295252)

	def __missing_args_embed(
			self, 
			ctx: commands.Context[commands.Bot]) -> Embed:
		embed = Embed(
			description = (
				f"* {ctx.author.name}, missing requires arugments\n" \
				f"* Usage:\n" \
				f"* `{prefix()}` blacklist `[USER_ID]` `(REASON)`\n" \
				f"* [] -> required argument\n" \
				f"* () -> optional argument\n" \
				f"* Example:\n" \
				f"* `{prefix()} blacklist 1234 bot abuse`"
			),
			color = 0xc1cfde,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(
			url = self.bot.user.avatar.url 
			if self.bot.user and self.bot.user.avatar
			else None
		)
			
		return embed

	def __success_embed(self, user: User, reason: Optional[str]) -> Embed:
		embed = Embed(
			description = (
				f"* Successfully blacklist: {user.name}\n" \
				f"* User ID: `{user.id}`\n" \
				f"* Reason `{reason if reason else 'No provided'}`"
			),
			color = 0xf2fac3,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(
			url = self.bot.user.avatar.url 
			if self.bot.user and self.bot.user.avatar
			else None
		)

		return embed

	def __already_blacklist(self, user: User) -> Embed:
		embed = Embed(
			description = (
				f"* User: {user.name} | `{user.id}` has been blacklisted."
			),
			color = 0xfac0b4,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(
			url = self.bot.user.avatar.url 
			if self.bot.user and self.bot.user.avatar
			else None
		)

		return embed

	@commands.command()
	@commands.is_owner()
	async def blacklist(
		self, 
		ctx: commands.Context[commands.Bot], 
		user: User, *, reason: Optional[str] = None) -> None:

		if not ctx.guild:
			return
		
		blacklist_user = self.bot.get_user(user.id)
		
		if blacklist_user:
			is_already_blacklist = await self.__blacklist_manager.is_blacklisted(blacklist_user.id)

			if is_already_blacklist == BlacklistResult.BLACKLISTED:
				await ctx.channel.send(embed = self.__already_blacklist(user = blacklist_user))
				return

			await self.__blacklist_manager.set_blacklist_user(blacklist_user.id)
			await ctx.channel.send(embed = self.__success_embed(user = user, reason = reason))

			if self.LOG_CHANNEL and isinstance(self.LOG_CHANNEL, TextChannel):
				now = int(datetime.now().timestamp())

				await self.LOG_CHANNEL.send(content = (
					f"**__Black List Notification:__**\n" \
					f"* By: {ctx.author.name} | `{ctx.author.id}`\n" \
					f"* Target: {user.name} | `{user.id}`\n" \
					f"* Reason: {reason if reason else 'No reason provided'}\n" \
					f"* Time: <t:{now}:R>"
				))

			return
		
		await ctx.channel.send(content = (
			f"* User: {user} not found"
		))

	@blacklist.error
	async def blacklist_error(
		self,
		ctx: commands.Context[commands.Bot],
		error: commands.CommandError) -> None:
		if not ctx.guild:
			return
		
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.channel.send(embed = self.__missing_args_embed(ctx = ctx))
			return
	
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(BlackListPrefix(bot = bot))