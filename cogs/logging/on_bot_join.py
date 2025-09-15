from discord.ext import commands
from discord import Guild
from core_utils.type_alias import (
	CanSendMessageChannel,
	DisableAllMentions
)

_CSMC = CanSendMessageChannel
_DAM = DisableAllMentions
class OnBotJoin(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.LOG_CHANNEL = self.bot.get_channel(1417157109195341904)

	@commands.Cog.listener()
	async def on_guild_join(self, guild: Guild) -> None:
		if isinstance(self.LOG_CHANNEL, _CSMC):
			await self.LOG_CHANNEL.send(content = (
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
				)}"
			), allowed_mentions = _DAM)
		
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(OnBotJoin(bot = bot))