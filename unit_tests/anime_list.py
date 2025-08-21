from json import load
from typing import Any, Optional 
from aiohttp import ClientSession
from asyncio import run

with open(file = "config/config.json", mode = "r", encoding = "utf-8") as config_file:
	data = load(config_file)
	MYANIMELIST_CLIENT_ID = data["MYANIMELIST_CLIENT_ID"]

async def anime_details(anime_id: int) -> Optional[Any]:
	headers = {
		"X-MAL-CLIENT-ID": MYANIMELIST_CLIENT_ID
	}
	params = {
		"fields": "id,title,main_picture,synopsis,studios"
	}

	URL = f"https://api.myanimelist.net/v2/anime/{anime_id}"

	async with ClientSession() as session:
		try:
			async with session.get(url = URL, params = params, headers = headers) as response:
				response.raise_for_status()

				data = await response.json()

				return data
		except Exception as error:
			print(f"Could not get anime details with error: {error}")
			return None

def anime_list_test() -> None:
	anime_info = run(anime_details(anime_id = 1))

	if anime_info:
		print(f"ID: {anime_info['id']}")
		print(f"Name: {anime_info['title']}")
		print(f"Image: {anime_info['main_picture']['large']}")
		print(f"Description: {anime_info['synopsis'][:250]}...")
		
		studios = anime_info.get('studios', [])
		studio_name = studios[0]['name'] if studios else 'unknown studio'
		print(f"Studio {studio_name}")
	
anime_list_test()