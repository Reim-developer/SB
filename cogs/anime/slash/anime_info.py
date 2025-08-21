from typing import Optional
from discord.ext import commands
from discord import (
	app_commands, Interaction, Embed, User, Member
)
from api.my_anime_list import MyAnimeListApi
from datetime import datetime
from api.types import MyAnimeList

class AnimeInfoSlash(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.my_anime_list_api = MyAnimeListApi()

	def __anime_not_found(self, anime_id: int, user: User | Member) -> Embed:
		embed = Embed(
			title = "Error",
			description = (
				f"* Your anime with id `{anime_id}` not found.\n" \
				"* Or our system is temporarily overloaded.\n" \
				"* Please try again later."
			),
			color = 0xf5eacb,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(
			url = user.avatar.url 
			if user.avatar else None
		)

		return embed

	def __anime_info(self, anime_info: Optional[MyAnimeList]) -> Embed:
		if anime_info:
			embed = Embed(
				title = f"`{anime_info.title }` Information",
				description = (
					"**__Description:__**\n" \
					f"{anime_info.description[:2000]}..."
				),
				color = 0xe6c7fc,
				timestamp = datetime.now()
			)
			embed.set_image(url = anime_info.image_url)

			return embed
		
		return Embed(
			title = "Error",
			description = "Could not find any information of this anime",
			timestamp= datetime.now(),
			color = 0xc0fcc7
		)

	@app_commands.command(
		name = "my_animelist_info", 
		description = "Get anime information from MyAnimeList")
	@app_commands.describe(
		anime_id = "The anime id"
	)
	@app_commands.checks.cooldown(1, 15, key = lambda i: i.user.id)
	async def anime_info(
			self, 
			interaction: Interaction, anime_id: int) -> None:
		if not interaction.guild:
			return 
		
		await interaction.response.defer()
		anime_info = await self.my_anime_list_api.anime_info(id_of_anime = anime_id)

		if not anime_info:
			await interaction.followup.send(
				embed = self.__anime_not_found(
					anime_id = anime_id,
					user = interaction.user
				)
			)
			return

		await interaction.followup.send(
			embed = self.__anime_info(
				anime_info = anime_info
			)
		)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(AnimeInfoSlash(bot = bot))