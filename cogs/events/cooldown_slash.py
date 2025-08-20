from discord import Interaction
from discord.app_commands import AppCommandError, CommandOnCooldown
from discord.ext import commands
from time import time
from asyncio import sleep

class CooldownSlashEvent(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.bot.tree.on_error = self.on_app_command_error
				
	@commands.Cog.listener()
	async def on_app_command_error(
			self, interaction: Interaction, 
			error: AppCommandError) -> None:
		
		if not interaction.guild:
			return
		
		if isinstance(error, CommandOnCooldown):
			when = int(time() + error.retry_after)


			await interaction.response.send_message(
				content = (
					f"* Nu!, {interaction.user.name}\n" \
					f"* Try again in <t:{when}:R>"
				), ephemeral =  True)
			await sleep(error.retry_after)
		
			try:
				await interaction.delete_original_response()
			except AppCommandError as error:
				print(f"Could not delete message with error: {error}")

			return

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(CooldownSlashEvent(bot = bot))