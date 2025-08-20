from discord import (
	app_commands, Interaction, TextChannel, Embed
)
from discord.ext import commands
from sql.sql_manager import SQLiteManager
from datetime import datetime

class SetConfessionSlash(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.sqlite_manager =  SQLiteManager("database/database.db")

	def __embed(self, channel: TextChannel) -> Embed:
		embed = Embed(
			description = (
				f"* Successfully setup confession to: {channel.mention}"
			),
			timestamp = datetime.now(),
			color = 0xfaeae1
		)
		embed.set_thumbnail(
			url = 
			self.bot.user.avatar.url 
			if self.bot.user and self.bot.user.avatar 
			else None
		)

		return embed

	@app_commands.command(
		name = "set_confession", 
		description = "Setup your confession channel")
	@app_commands.describe(channel = "Channel you want setup confession channel")
	@app_commands.checks.cooldown(1, 15, key = lambda i: i.user.id)
	@app_commands.default_permissions(administrator = True)
	async def confession(
			self, interaction: Interaction,
			channel: TextChannel) -> None:
		
		guild = interaction.guild
		if not guild:
			return
		
		await self.sqlite_manager.set_confession_channel(
			guild_id = guild.id, channel_id = channel.id
		)

		await interaction.response.defer()
		await interaction.followup.send(embed = self.__embed(channel = channel))

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(SetConfessionSlash(bot = bot))