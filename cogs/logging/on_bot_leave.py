from typing import LiteralString
from discord.ext import commands
from discord.guild import Guild
from core_utils.type_alias import (
	CanSendMessageChannel, DisableAllMentions
)
from sql.sql_manager import SQLiteManager

_LTS = LiteralString
_CSMC 			  = CanSendMessageChannel
_SQL 		 	  = SQLiteManager
_DB: _LTS 		  = "database/database.db"
_DAM 			  =  DisableAllMentions
_SB_TABLE_NAME: _LTS = "sb_bot"

class OnBotLeaveLogging(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.LOG_CHANNEL = self.bot.get_channel(1410300232348078093)
		self.__sql_manager = _SQL(_DB)

	async def __clear_data(self, guild_id: int) -> None:
		await self.__sql_manager.exec(
			query = 
				f"""--sql
					DELETE FROM {_SB_TABLE_NAME} WHERE guild_id = ?
				""", parameters = (guild_id,)
		)

	@commands.Cog.listener()
	async def on_guild_remove(self, guild: Guild) -> None:
		if isinstance(self.LOG_CHANNEL, _CSMC):
			await self.__clear_data(guild_id = guild.id)
			await self.LOG_CHANNEL.send(
				content = (
					f"**__Bot Leave Notification:__**\n" \
					f"* Guild name: **{guild.name}**\n" \
					f"* Guild ID: `{guild.id}`\n" \
					f"* Current Guild Count: `{len(self.bot.guilds)}` guild"
				),
				allowed_mentions = _DAM
			)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(OnBotLeaveLogging(bot = bot))