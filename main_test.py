from json import load 
from discord import Intents, Status, Game
from discord.ext import commands, tasks
from sql.sql_manager import SQLiteManager
from widgets.confession_widget import ReplyWidget
from core_utils.giveaway_timer import GiveawayTimer, TimerData

with open(file = "./config/config.test.json", mode = "r", encoding = "utf-8") as config_file:
	json_data = load(config_file)
	BOT_TOKEN = json_data["BOT_TOKEN"]
	BOT_PREFIX = json_data["BOT_PREFIX"]

SHARD_COUNT =  2
bot_intents = Intents.all()

async def __setup_cogs() -> None:
	cog_list = [
		"cogs.events.cooldown",
		"cogs.events.cooldown_slash",
		"cogs.logging.on_bot_leave",
		"cogs.logging.on_bot_join",
		"cogs.utils.prefix.invite",
		"cogs.utils.prefix.avatar",
		"cogs.utils.prefix.help",
		"cogs.utils.prefix.member_count",
		"cogs.utils.prefix.server_info",
		"cogs.utils.slash.set_confession",
		"cogs.utils.slash.confession",
		"cogs.utils.slash.giveaway",
		"cogs.utils.slash.giveaway_reroll",
		"cogs.utils.slash.embed_builder",
		"cogs.owner.prefix.blacklist",
		"cogs.owner.prefix.unblacklist",
		"cogs.owner.prefix.sync_slash",
		"cogs.anime.slash.anime_info"
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
	shard_ids = [0, 1],
)

@tasks.loop(minutes = 5)
async def update_presence() -> None:
	await bot.change_presence(
		status = Status.online,
		activity = Game(name = f"With {len(bot.users)} users | {len(bot.guilds)} servers")
	)
	
	print(f"Online as: {bot.user.name if bot.user else  'unknown bot name'}")
	print(f"Shard Count: {bot.shard_count}")
	print(f"Shard IDs: {list(bot.shards.keys()) if bot.shards else 'No shards'}")
	print(f"On: {len(bot.guilds)} servers")
	print(f"On: {len(bot.users)} members")	

@bot.event
async def on_ready() -> None:
	await __setup_cogs()
	await bot.tree.sync()
	bot.add_view(view = ReplyWidget(bot = bot))

	sqlite_manager = SQLiteManager("database/database.db")
	await sqlite_manager.init_if_not_exists()
	await GiveawayTimer(TimerData(bot = bot, sqlite_manager = sqlite_manager)).load_active_gws()

	await update_presence.start()

bot.run(token = BOT_TOKEN)