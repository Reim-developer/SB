from discord.ext import commands
from discord.guild import Guild
from discord import AllowedMentions
from core_utils.type_alias import CanSendMessageChannel

_CSMC = CanSendMessageChannel
_AL = AllowedMentions

class OnBotLeaveLogging(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.LOG_CHANNEL = self.bot.get_channel(1410300232348078093)

	@commands.Cog.listener()
	async def on_guild_remove(self, guild: Guild) -> None:
		if isinstance(self.LOG_CHANNEL, _CSMC):
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