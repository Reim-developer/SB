from discord import (
	app_commands, Interaction, TextChannel, Embed
)
from discord.ext import commands
from core_utils.container import container_instance
from sql.confession_manager import ConfessionManager
from datetime import datetime

class SetConfessionSlash(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.__pool = container_instance.get_postgres_manager().pool
		assert self.__pool is not None
		self.__confession_manager = ConfessionManager(self.__pool)


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
		
		await self.__confession_manager.set_confession_channel(
			guild_id = guild.id, channel_id = channel.id
		)

		await interaction.response.defer()
		await interaction.followup.send(embed = self.__embed(channel = channel))

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(SetConfessionSlash(bot = bot))