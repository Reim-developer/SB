from dataclasses import dataclass, fields
from discord.ext import commands
from discord import app_commands, Interaction
from widgets.embed_builder_widget import (
	EmbedBuilderWidget, ImageData
)
from enum import Enum
from typing import Optional, Tuple, TypeAlias
from core_utils.url import URLUtils

class Result(Enum):
	Ok 	= 0
	Err = 1

_EBW:     TypeAlias 	= EmbedBuilderWidget
_IMG: 	  TypeAlias 	= ImageData
_URL_ERR: TypeAlias 	= Tuple[Result, Optional[str]]

@dataclass
class _ImageField:
	image: Optional[str]
	thumbnail: Optional[str]
	footer_icon: Optional[str]
	author_icon: Optional[str]

class EmbedBuilderSlash(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	def __is_url(self, image_field: _ImageField) -> _URL_ERR:
		U = URLUtils
		R = Result

		urls = (
			getattr(image_field, field.name)
			for field in fields(image_field)
		)

		for url in urls:
			if url and not U.valid_url(url):
				return R.Err, url
			
		return R.Ok, None

	@app_commands.command(
		name = "embed_builder",
		description = "Create & send embed"
	)
	@app_commands.describe(
		embed_image = "Embed image URL",
		thumbnail_image = "Thumbnail image URL",
		footer_icon = "Footer icon URL",
		author_icon = "Author icon URL"
	)
	@app_commands.checks.has_permissions(administrator = True)
	@app_commands.checks.bot_has_permissions(administrator = True)
	async def embed_builder(
			self, interaction: Interaction,
			embed_image: Optional[str] = None,
			thumbnail_image: Optional[str] = None,
			footer_icon: Optional[str] = None,
			author_icon: Optional[str] = None) -> None:
		if not interaction.guild:
			await interaction.response.send_message(
				content = (
					"Could not use this command in DM"
				),
				ephemeral = True
			)
			return
		
		I  = _ImageField
		result, err_url = self.__is_url(I(
			image 		= embed_image,
			thumbnail 	= thumbnail_image,
			footer_icon = footer_icon,
			author_icon = author_icon
		))

		if result == Result.Err:
			await interaction.response.send_message(
				content = (
					"* Could not create embed image with error:\n" \
					"**Embed image not found, or does not exists**\n" \
					f"""
```diff
- Invalid embed image URL
{err_url if err_url else 'Unknown URL'}
^^^ Please check this URL and try again
```
					"""
				),
				ephemeral = True
			)
			return
		
		await interaction.response.send_modal(
			_EBW(
				bot 			= self.bot,
				image_data 		= _IMG(
					image 		= embed_image,
					thumbnail 	= thumbnail_image,
					footer_icon = footer_icon,
					author_icon = author_icon
				)
			),
		)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(EmbedBuilderSlash(bot = bot))