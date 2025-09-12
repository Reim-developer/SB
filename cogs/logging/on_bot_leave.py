from typing import LiteralString
from discord.ext import commands
from discord.guild import Guild
from discord import AllowedMentions
from core_utils.type_alias import CanSendMessageChannel
from sql.sql_manager import SQLiteManager

_CSMC = CanSendMessageChannel
_AL = AllowedMentions
_SQL = SQLiteManager
_DB: LiteralString = "database/database.db"
_TABLE_NAME: LiteralString = "sb_bot"

class OnBotLeaveLogging(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.LOG_CHANNEL = self.bot.get_channel(1410300232348078093)
		self.__sql_manager = _SQL(_DB)

	@commands.Cog.listener()
	async def on_guild_remove(self, guild: Guild) -> None:
		if isinstance(self.LOG_CHANNEL, _CSMC):
			await self.__sql_manager.exec(
				query = f"""--sql
					DELETE FROM {_TABLE_NAME} WHERE guild_id = ?
				""", parameters = (guild.id,)
			)
			await self.LOG_CHANNEL.send(
				content = (
					f"**__Bot Leave Notification:__**\n" \
					f"* Guild name: **{guild.name}**\n" \
					f"* Guild ID: `{guild.id}`\n" \
					f"* Current Guild Count: `{len(self.bot.guilds)}` guild"
				),
				allowed_mentions = _AL(
					everyone = False,
					users = False,
					roles = False
				)
			)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(OnBotLeaveLogging(bot = bot))