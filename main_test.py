from json import load 
from discord import Intents
from discord.ext import commands
from sql.sql_manager import SQLiteManager

with open(file = "./config/config.test.json", mode = "r", encoding = "utf-8") as config_file:
	json_data = load(config_file)
	BOT_TOKEN = json_data["BOT_TOKEN"]
	BOT_PREFIX = json_data["BOT_PREFIX"]

bot_intents = Intents.all()
bot_intents.presences = False

async def __setup_cogs() -> None:
	cog_list = [
		"cogs.events.cooldown",
		"cogs.events.cooldown_slash",
		"cogs.utils.prefix.invite",
		"cogs.utils.prefix.avatar",
		"cogs.utils.prefix.help",
		"cogs.utils.prefix.member_count",
		"cogs.utils.slash.set_confession",
		"cogs.utils.slash.confession"
	]

	for cog in cog_list:
		try:
			await bot.load_extension(cog)
			print(f"Load cog: {cog} successfully")

		except Exception as error:
			print(f"Could not load cog: {cog} with error: {error}")

bot = commands.Bot(
	command_prefix = BOT_PREFIX, 
	help_command = None, 
	intents = bot_intents,
	case_insensitive = True
)

@bot.event
async def on_ready() -> None:
	await __setup_cogs()
	await bot.tree.sync()
	await SQLiteManager("database/database.db").init_if_not_exists()
	print(f"Online as: {bot.user.name if bot.user else  'unknown bot name'}")

bot.run(token = BOT_TOKEN)