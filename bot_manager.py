from discord.ext 			   import tasks
from typing                    import List
from discord.ext 		       import commands
from discord 			  	   import Intents, Game, Status
from core_utils.giveaway_timer import GiveawayTimer, TimerData
from core_utils.prefixes       import prefixes
from json 				       import load
from core_utils.logging        import Log
from core_utils.container      import container_instance
from widgets.confession_widget import ReplyWidget

class _PropsManager:
	_DEV_SHARDS  = 2
	_PROC_SHARDS = 3

	def __init__(self, dev_mode: bool) -> None:
		self.__dev_mode = dev_mode

	async def setup_cogs(self, bot: commands.AutoShardedBot) -> None:
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
				Log.info(f"Load cog: {cog} successfully")

			except Exception as error:
				Log.critical(f"Could not load cog: {cog} with error: {error}")

	def setup_intents(self) -> Intents:
		if self.__dev_mode:
			intents = Intents.all()
			return intents
		
		intents 		  = Intents.all()
		intents.presences = False
		return intents

	def setup_shards(self) -> int:
		return (
			self._DEV_SHARDS 
			if self.__dev_mode else self._PROC_SHARDS
		)
	
	def setup_shard_ids(self) -> List[int]:
		return (
			[0, 1] 
			if self.__dev_mode 
			else [0, 1, 2]
		)

class _Presence:
	def __init__(self, bot: commands.AutoShardedBot) -> None:
		self.bot = bot

	@tasks.loop(minutes = 5)
	async def update_presence(self) -> None:
		await self.bot.change_presence(
			status = Status.online,
			activity = Game(name = (
				f"With {len(self.bot.users)} users | "
				f"{len(self.bot.guilds)} servers"
			))
		)
		
		Log.info(f"Online as: {self.bot.user.name if self.bot.user else  'unknown bot name'}")
		Log.info(f"Shard Count: {self.bot.shard_count}")
		Log.info(f"Shard IDs: {list(self.bot.shards.keys()) if self.bot.shards else 'No shards'}")
		Log.info(f"On: {len(self.bot.guilds)} servers")
		Log.info(f"On: {len(self.bot.users)} members")	

class BotManager(commands.AutoShardedBot):
	def __init__(self, dev_mode: bool) -> None:
		self.__dev_mode      = dev_mode
		self.__props_manager = _PropsManager(self.__dev_mode)

		super().__init__(
			command_prefix     = prefixes,
			intents 	  	   = self.__props_manager.setup_intents(),
			help_command 	   = None,
			case_insensitive   = True,
			strip_after_prefix = True,
			shard_count 	   = self.__props_manager.setup_shards(),
			shard_ids 		   = self.__props_manager.setup_shard_ids(),
		)

	async def on_ready(self) -> None:
		postgres_manager = container_instance.get_postgres_manager()

		await postgres_manager.init_if_not_exists()
		await self.__props_manager.setup_cogs(self)
		await self.tree.sync()

		await GiveawayTimer(TimerData(
			bot = self, postgres_manager = postgres_manager
		)).load_active_gws()
		

		await _Presence(self).update_presence.start()
		self.add_view(view = ReplyWidget(self))

	def __load_cfg(self) -> str:
		DEV_PATH  = "config/config.test.json"
		PROD_PATH = "config/config.json"

		with open(
			file = (
				DEV_PATH 
				if self.__dev_mode 
				else PROD_PATH
			), 
			mode = "r", encoding = "utf-8") as cfg:
			data = load(cfg)

		return data["BOT_TOKEN"]

	def bot_run(self) -> None:
		self.run(token = self.__load_cfg())
