from typing import Any, Optional
from json_helper import myanimelist_clientid
from aiohttp import ClientSession

class MyAnimeListApi:
	def __init__(self, anime_id: int) -> None:
		self.anime_id = anime_id
		self.__PARAMS = {
			"fields": "id,title,main_picture,synopsis,studios"
		}
		self.__HEADERS = {
			"X-MAL-CLIENT-ID": myanimelist_clientid()
		}
		self.__API_URL = f"https://api.myanimelist.net/v2/anime/{anime_id}"

	async def anime_info(self) -> Optional[Any]:
		async with ClientSession() as session:
			try:
				async with session.get(
						url = self.__API_URL, 
						params = self.__PARAMS, 
						headers = self.__HEADERS) as response:
					response.raise_for_status()

					data = await response.json()

					return data
			except Exception as error:
				print(f"Could not get anime details with error: {error}")
				return None