from discord.abc import GuildChannel
from discord import (
	Interaction, app_commands, Embed, Guild,
	TextChannel
)
from discord.ext import commands
from sql.sql_manager import SQLiteManager
from datetime import datetime
from asyncio import sleep
from datetime import datetime

class ConfessionSlash(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.sqlite_manager = SQLiteManager("database/database.db")
		self.LOG_CHANNEL = 1057274847459295252

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
	
	def __confession_embed(self, msg: str) -> Embed:
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

		return embed

	@app_commands.command(
		name = "confession", 
		description = "Send confession to confession channel"
	)
	@app_commands.describe(message = "The message you want to send")
	@app_commands.checks.cooldown(1, 15, key = lambda i: i.user.id)
	async def confession(
			self, interaction: Interaction, 
			message: str) -> None:
		guild = interaction.guild
		if not guild:
			return
		
		await interaction.response.defer(ephemeral = True)
		channel_id = await self.sqlite_manager.confession_channel(guild_id = guild.id)
		
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
		
		await interaction.followup.send(content = (
			f"Successfully send your confession to: {guild_channel.mention}"
		))

		if isinstance(guild_channel, TextChannel):
			msg = await guild_channel.send(embed = self.__confession_embed(msg = message))
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

				try:
					await LOG_CHANNEL.send(content = (
						f"* Message content: {message}\n" \
						f"* Author ID: `{interaction.user.id}`\n" \
						f"* Time: <t:{time_now}:R>"
					))
				
				except Exception as e:
					print(e)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(ConfessionSlash(bot = bot))