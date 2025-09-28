from json import load 
from discord import Intents, Status, Game
from discord.ext import commands, tasks
from core_utils.container import container_instance
from core_utils.prefixes import prefixes
from widgets.confession_widget import ReplyWidget
from core_utils.giveaway_timer import GiveawayTimer, TimerData

# Todo: Removed this in future 
# and implement class `MainBot` or `ClientManager`...
with open(file = "./config/config.json", mode = "r", encoding = "utf-8") as config_file:
	json_data = load(config_file)
	BOT_TOKEN = json_data["BOT_TOKEN"]
	# BOT_PREFIX = json_data["BOT_PREFIX"] # Removed, use `prefixes` instead 

SHARD_COUNT 		  = 3
bot_intents 		  = Intents.all()
bot_intents.presences = False

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
		"cogs.utils.slash.set_confession",
		"cogs.utils.slash.confession",
		"cogs.utils.slash.giveaway",
		"cogs.utils.slash.giveaway_reroll",
		"cogs.owner.prefix.blacklist",
		"cogs.owner.prefix.unblacklist",
		"cogs.owner.prefix.sync_slash",
		"cogs.utils.slash.embed_builder",
		"cogs.anime.slash.anime_info"
	]

	for cog in cog_list:
		try:
			await bot.load_extension(cog)
			print(f"Load cog: {cog} successfully")

		except Exception as error:
			print(f"Could not load cog: {cog} with error: {error}")

bot = commands.AutoShardedBot(
	command_prefix = prefixes, 
	help_command = None, 
	intents = bot_intents,
	case_insensitive = True,
	shard_count = SHARD_COUNT,
	shard_ids = [0, 1, 2]
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
	postgres_manager = container_instance.get_postgres_manager()
	await postgres_manager.init_if_not_exists()
	
	await __setup_cogs()
	await bot.tree.sync()
	bot.add_view(view = ReplyWidget(bot = bot))

	await GiveawayTimer(TimerData(
		bot = bot, postgres_manager = postgres_manager
	)).load_active_gws()

	await update_presence.start()

bot.run(token = BOT_TOKEN)