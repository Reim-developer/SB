from discord.ext           import commands
from discord.guild         import Guild
from core_utils.type_alias import (
	CanSendMessageChannel, DisableAllMentions
)
from core_utils.container import container_instance
from sql.tables 		  import Tables
from psycopg.sql 		  import SQL, Identifier

_CSMC 			  = CanSendMessageChannel
_DAM 			  =  DisableAllMentions

class OnBotLeaveLogging(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.LOG_CHANNEL = self.bot.get_channel(1410300232348078093)
		self.__pool = container_instance.get_postgres_manager().pool

	async def __clear_data(self, guild_id: int) -> None:
		assert self.__pool is not None

		async with self.__pool.connection() as connection:
			await connection.execute(
				SQL("DELETE FROM {} WHERE guild_id = %s")
				.format(Identifier(Tables.GUILDS)),
			(guild_id,))

	@commands.Cog.listener()
	async def on_guild_remove(self, guild: Guild) -> None:
		if isinstance(self.LOG_CHANNEL, _CSMC):
			await self.__clear_data(guild_id = guild.id)
			await self.LOG_CHANNEL.send(
				content = (
					f"**__Bot Leave Notification:__**\n" \
					f"* Guild name: **{guild.name}**\n" \
					f"* Guild Member Count: {(
						f'`{guild.member_count}` Member(s)' 
						if guild.member_count 
						else '`Unknown Member Count`'
					)}\n" \
					f"* Guild ID: `{guild.id}`\n" \
					f"* Current Guild Count: `{len(self.bot.guilds)}` guild"
				),
				allowed_mentions = _DAM
			)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(OnBotLeaveLogging(bot = bot))