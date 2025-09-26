from typing import Optional
from discord.abc import GuildChannel
from discord import (
	Interaction, app_commands, Embed, Guild,
	TextChannel, 
)
from discord.ext import commands
from core_utils.container import container_instance
from sql.confession_manager import ConfessionManager
from sql.blacklist_manager import BlacklistManager, BlacklistResult
from datetime import datetime
from asyncio import sleep
from datetime import datetime
from widgets.confession_widget import ReplyWidget
from core_utils.url import URLUtils

class ConfessionSlash(commands.Cog):
	_MAX_IMAGE_URL_LENGTH = 250

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.LOG_CHANNEL = 1057274847459295252

		self.__pool = container_instance.get_postgres_manager().pool
		assert self.__pool is not None
		self.__confession_manager = ConfessionManager(self.__pool)
		self.__blacklist_manager  = BlacklistManager(self.__pool)

	def __not_set_embed(self) -> Embed:
		embed = Embed(
			description = "* The server has not setup any confession channels yet",
			color = 0xf5e4b5,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(
			url = self.bot.user.avatar.url 
			if self.bot.user and self.bot.user.avatar
			else None
		)

		return embed
	
	def __channel_not_found_embed(self) -> Embed:
		embed = Embed(
			description = (
				"* Channel does not exist. Please reset via slash command:\n",
				"* /set_confession"
			),
			color = 0xf5e4b5,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(
			url = self.bot.user.avatar.url 
			if self.bot.user and self.bot.user.avatar
			else None
		)

		return embed
	
	def __missing_permissions_embed(self) -> Embed:
		embed = Embed(
			description = (
				"* Could not send message to this channel\n" \
				"* I need the following permissions:\n" \
				"* `[MANAGE_THREADS]` | `[ADD_REACTIONS]` | `[SEND_MESSAGES]`"
			),
			color = 0xf5e4b5,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(
			url = self.bot.user.avatar.url 
			if self.bot.user and self.bot.user.avatar
			else None
		)

		return embed
	
	async def __can_send_message(
			self, guild: Guild,
			guild_channel: GuildChannel) -> bool:
		bot_user = self.bot.user
		if bot_user:
			bot_member = guild.get_member(bot_user.id)

			if bot_member:
				msg_perm = guild_channel.permissions_for(bot_member)

				if msg_perm.embed_links and \
					msg_perm.add_reactions and \
					msg_perm.send_messages and \
					msg_perm.manage_threads:

					return True

		return False
	
	def __confession_embed(self, msg: str, image_url: Optional[str]) -> Embed:
		embed = Embed(
			title = f"Anonymous Confession",
			description = (
				f"{msg}"
			),
			color = 0xb2e1eb,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(
			url = self.bot.user.avatar.url 
			if self.bot.user and self.bot.user.avatar
			else None
		)
		embed.set_image(
			url = image_url if image_url else None
		)

		return embed

	@app_commands.command(
		name = "confession", 
		description = "Send confession to confession channel"
	)
	@app_commands.describe(
		message   = "The message you want to send",
		image_url = "Your image URL (Optional)"
	)
	@app_commands.checks.cooldown(1, 15, key = lambda i: i.user.id)
	async def confession(
			self, interaction: Interaction, 
			message: str, image_url: Optional[str] = None) -> None:
		guild = interaction.guild
		if not guild:
			return
		
		user = interaction.user
		is_blacklist = self.__blacklist_manager.is_blacklisted(user.id)

		if await is_blacklist == BlacklistResult.BLACKLISTED:
			await interaction.response.send_message(
				content = (
					f"Hello, {interaction.user.name}\n" \
					"Sorry but you have been blacklisted, details " \
					"please join our support server to appeal\n" \
					"https://discord.gg/S9Z4uUmXbA"
				),
				ephemeral = True
			)
			return
		
		await interaction.response.defer(ephemeral = True)
		channel_id = await self.__confession_manager.get_confession_channel(
			guild_id = guild.id
		)
		
		if not channel_id:
			await interaction.followup.send(embed = self.__not_set_embed())
			return
	
		guild_channel = guild.get_channel(channel_id)
		if not guild_channel:
			await interaction.followup.send(embed = self.__channel_not_found_embed())
			return
		
		can_send_msg = await self.__can_send_message(
			guild = guild, 
			guild_channel = guild_channel
		)

		if not can_send_msg:
			await interaction.followup.send(embed = self.__missing_permissions_embed())
			return
		
		if image_url and not URLUtils.valid_url(url = image_url):
			await interaction.followup.send(
				f"* Image URL: `{image_url}` is not valid, please try again",
				ephemeral = True
			)
			return
		
		if image_url and len(image_url) >= self._MAX_IMAGE_URL_LENGTH:
			await interaction.followup.send(
				f"* Max length of image URL is: `{self._MAX_IMAGE_URL_LENGTH}` "
				"characters, please try again",
				ephemeral = True
			)
			return
		
		await interaction.followup.send(content = (
			f"Successfully send your confession to: {guild_channel.mention}"
		))

		if isinstance(guild_channel, TextChannel):
			msg = await guild_channel.send(
				embed = self.__confession_embed(
					msg = message, image_url = image_url
				),
				view = ReplyWidget(self.bot)
			)
			await msg.create_thread(
				name = "What do you about this confession?",
				auto_archive_duration = 1440
			)
			await sleep(0.5)
			await msg.add_reaction("👍")
			await msg.add_reaction("👎")

			LOG_CHANNEL = self.bot.get_channel(self.LOG_CHANNEL)
			if LOG_CHANNEL and isinstance(LOG_CHANNEL, TextChannel):
				time_now = int(datetime.now().timestamp())

				await LOG_CHANNEL.send(content = (
					f"* Message content: {message}\n"
					f"* Image URL: {(
						image_url if image_url else 'No Image'
					)}\n"
					f"* Author ID: `{interaction.user.id}`\n"
					f"* Time: <t:{time_now}:R>"
				))
				
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(ConfessionSlash(bot = bot))