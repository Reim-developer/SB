from dataclasses import dataclass

@dataclass
class MyAnimeList:
	id: int
	title: str
	image_url: str
	studio_name: str
	description: str