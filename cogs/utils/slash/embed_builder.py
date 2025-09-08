from discord.ext import commands
from discord import app_commands, Interaction
from widgets.embed_builder_widget import EmbedBuilderWidget
from typing import TypeAlias

_EBW: TypeAlias = EmbedBuilderWidget
class EmbedBuilderSlash(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	@app_commands.command(
		name = "embed_builder",
		description = "Create & send embed"
	)
	@app_commands.checks.has_permissions(administrator = True)
	@app_commands.checks.bot_has_permissions(administrator = True)
	async def embed_builder(self, interaction: Interaction) -> None:
		if not interaction.guild:
			await interaction.response.send_message(
				content = (
					"Could not use this command in DM"
				),
				ephemeral = True
			)
			return
		
		await interaction.response.send_modal(_EBW(bot = self.bot))

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(EmbedBuilderSlash(bot = bot))