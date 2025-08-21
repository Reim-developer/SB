from json import load

def emoji(query: str) -> str:
	with open(file = "config/emojis.json", mode = "r", encoding = "utf-8") as emojis_file:
		data = load(emojis_file)
		
	if not data[query]:
		raise ValueError(f"Emoji {query} is not exists.")

	return data[f"{query}"]

def prefix() -> str:
	with open(file = "config/config.json", mode = "r", encoding = "utf-8") as emojis_file:
		data = load(emojis_file)
	
	return data["BOT_PREFIX"]

def myanimelist_clientid() -> str:
	with open(file = "config/config.json", mode = "r", encoding = "utf-8") as config_file:
		data = load(config_file)

	return data["MYANIMELIST_CLIENT_ID"]