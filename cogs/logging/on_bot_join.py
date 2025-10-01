from discord.ext           import commands
from discord               import Guild
from core_utils.type_alias import (
	CanSendMessageChannel,
	DisableAllMentions
)
from core_utils.container  import container_instance
from psycopg.sql		   import SQL, Identifier

from sql.tables 		   import Tables
from core_utils.logging    import Log

_CSMC = CanSendMessageChannel
_DAM = DisableAllMentions
class OnBotJoin(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot 		   = bot
		self.__LOG_CHANNEL = self.bot.get_channel(1417157109195341904)
		self.__pool 	   = container_instance.get_postgres_manager().pool

	async def __add_guild(self, guild_id: int) -> None:
		assert self.__pool is not None
		try:
			async with self.__pool.connection() as connection:
				await connection.execute(
					SQL("INSERT INTO {} (guild_id) VALUES (%s) ON CONFLICT "
					"(guild_id) DO NOTHING").format(Identifier(Tables.GUILDS)),
					(guild_id,)
				)

		except Exception as error:
			Log.critical(
				f"Could not add guild ID: {guild_id} "
				f"with error: {error}"
			)


	@commands.Cog.listener()
	async def on_guild_join(self, guild: Guild) -> None:
		await self.__add_guild(guild_id = guild.id)

		if isinstance(self.__LOG_CHANNEL, _CSMC):
			await self.__LOG_CHANNEL.send(content = (
				"**__Bot Add Notification__:**\n"
				f"* Guild Name: {guild.name}\n"
				f"* Guild ID: `{guild.id}`\n"
				f"* Create At: <t:{(
					int(guild.created_at.timestamp())
				)}:R>\n"
				f"* Owner ID: `{(
					guild.owner_id 
					if guild.owner_id else 'Unknown Owner ID'
				)}`\n"
				f"* Owner Name: {(
					guild.owner.name
					if guild.owner else 'Unknown Owner Name'
				)}\n"
				f"* Member Count: {(
					f"`{guild.member_count}` Member(s)"
					if guild.member_count
					else '`Unknown Member Count`'
				)}"
			), allowed_mentions = _DAM)
		
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(OnBotJoin(bot = bot))