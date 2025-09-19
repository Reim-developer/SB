from dataclasses import dataclass
from discord.ui import View, Button
from discord.ui.button import V
from discord import ButtonStyle
from typing import Optional, Self

@dataclass
class GuildAssets:
	icon_url: 	Optional[str]
	banner_url: Optional[str]

_BS 		 = ButtonStyle
_B  		 = Button[V]
_DISCORD_URL = "https://discord.com"
class DownloadGuildAssetsWidget(View):
	_G = GuildAssets

	def __init__(self, assets: _G) -> None:
		super().__init__(timeout = None)
		self.__assets = assets

		self.add_item(_B[Self](
			style 	 = _BS.url,
			disabled = (
				True 
				if not self.__assets.banner_url else False
			),
			label = (
				"No Server Banner"
				if not self.__assets.banner_url else 
				"Download Server Banner"
			),
			url = (
				self.__assets.banner_url
				if self.__assets.banner_url else _DISCORD_URL
			)
		))

		self.add_item(_B[Self](
			style 	 = _BS.url,
			disabled = (
				True
				if not self.__assets.icon_url else False
			),
			label = (
				"No Server Icon"
				if not self.__assets.icon_url else
				"Download Server Icon"
			),
			url = (
				self.__assets.icon_url
				if self.__assets.icon_url else _DISCORD_URL
			)
		))