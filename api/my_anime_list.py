from typing import Optional
from json_helper import myanimelist_clientid
from aiohttp import ClientSession
from .types import MyAnimeList

class MyAnimeListApi:
	def __init__(self) -> None:
		self.__PARAMS = {
			"fields": "id,title,main_picture,synopsis,studios"
		}
		self.__HEADERS = {
			"X-MAL-CLIENT-ID": myanimelist_clientid()
		}

	async def anime_info(self, id_of_anime: int) -> Optional[MyAnimeList]:
		API_URL = f"https://api.myanimelist.net/v2/anime/{id_of_anime}"

		async with ClientSession() as session:
			M = MyAnimeList

			try:
				async with session.get(
						url = API_URL, 
						params = self.__PARAMS, 
						headers = self.__HEADERS) as response:
					response.raise_for_status()

					data = await response.json()

					studios = data.get('studios', [])
					studio_name = studios[0]['name'] if studios else 'unknown studio'

					return M (
						id = data.get('id', 'unknown description'),
						title = data.get('title', 'unknown description'),
						image_url = data['main_picture']['large'],
						studio_name = studio_name,
						description = data.get('synopsis', 'unknown description')
					)

			# We will ignore the exception in production
			# It is better way return `None` for handle errors  the in command.
			except:
				return None