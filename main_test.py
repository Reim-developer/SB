from json import load 
from discord import Intents
from discord.ext import commands
from sql.sql_manager import SQLiteManager
from asyncio import run

with open(file = "./config/config.test.json", mode = "r", encoding = "utf-8") as config_file:
	json_data = load(config_file)
	BOT_TOKEN = json_data["BOT_TOKEN"]
	BOT_PREFIX = json_data["BOT_PREFIX"]

SHARD_COUNT =  2
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
		"cogs.utils.slash.confession",
		"cogs.owner.prefix.blacklist",
		"cogs.owner.prefix.unblacklist"
	]

	for cog in cog_list:
		try:
			await bot.load_extension(cog)
			print(f"Load cog: {cog} successfully")

		except Exception as error:
			print(f"Could not load cog: {cog} with error: {error}")

bot = commands.AutoShardedBot(
	command_prefix = BOT_PREFIX, 
	help_command = None, 
	intents = bot_intents,
	case_insensitive = True,
	shard_count = SHARD_COUNT,
	shard_ids = [0, 1]
)

@bot.event
async def on_ready() -> None:
	await __setup_cogs()
	await SQLiteManager("database/database.db").init_if_not_exists()
	await bot.tree.sync()

	print(f"Online as: {bot.user.name if bot.user else  'unknown bot name'}")
	print(f"Shard Count: {bot.shard_count}")
	print(f"Shard IDs: {list(bot.shards.keys()) if bot.shards else 'No shards'}")
	print(f"On: {len(bot.guilds)} servers")
	print(f"On: {len(bot.users)} members")


async def main() -> None:
	async with bot:
		await bot.start(token = BOT_TOKEN)

try:
	run(main())

except KeyboardInterrupt:
	print("\nCanceled.")