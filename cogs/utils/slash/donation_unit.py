from dataclasses import dataclass
from discord.ext import commands
from discord import app_commands, Interaction, Embed
from core_utils.container import container_instance
from sql.donation_manager import DonationManager
from core_utils.type_alias import CanSendMessageChannel
from datetime import datetime 
from core_utils.time_utils import TimeUtils

_CSMC = CanSendMessageChannel

@dataclass
class _UnitModifyContext:
	channel_id:  int
	interaction: Interaction
	money_unit:  str

class DonationUnitSlash(commands.Cog):
	_MIN_UNIT_LENGTH = 10

	def __init__(self, bot: commands.Bot) -> None:
		self.bot  = bot
		self.pool = container_instance.get_postgres_manager().pool

		assert self.pool is not None
		self.donation_manager = DonationManager(self.pool)

	async def __send_log_unit_modify(self, ctx: _UnitModifyContext) -> None:
		assert ctx.interaction.guild is not None # Interaction.guild will always not `None` here

		channel = ctx.interaction.guild.get_channel(ctx.channel_id)
		if channel and isinstance(channel, _CSMC):
			await channel.send(
				embed = Embed(
					title       = "Server Money Unit Modify",
					description = (
						f"* By: {ctx.interaction.user.name}\n"
						f"* ID: `{ctx.interaction.user.id}`\n" 
						f"* At: <t:{TimeUtils.unix_time()}:R>\n"
						f"* Modify To: `{ctx.money_unit}`"
					),
					color = 0xc0ff9e
				)
			)

	@app_commands.command(
		name = "donation_unit_set", 
		description = "Set money unit of donation system")
	@app_commands.describe(
		money_unit = "Money unit of donation"
	)
	@app_commands.checks.cooldown(rate = 1, per = 15, key = lambda i: i.user.id)
	@app_commands.checks.bot_has_permissions(administrator = True)
	@app_commands.default_permissions(administrator = True)
	async def donation_unit_set(self, 
							 interaction: Interaction, money_unit: str) -> None:
		if not interaction.guild:
			await interaction.response.send_message(
				"Could not use this command in DM"
			)
			return 
		
		if len(money_unit) >= self._MIN_UNIT_LENGTH:
			await interaction.response.send_message(
				f"Could not set money unit over {self._MIN_UNIT_LENGTH} characters",
				ephemeral = True
			)
			return
		
		await interaction.response.defer()

		await self.donation_manager.set_money_unit(
			guild_id   = interaction.guild.id,
			money_unit = money_unit
		)

		channel_id = await self.donation_manager.get_log_channel(
			guild_id = interaction.guild.id
		)
		if channel_id:
			await self.__send_log_unit_modify(_UnitModifyContext(
				channel_id  = channel_id,
				interaction = interaction,
				money_unit  = money_unit
			))

		await interaction.followup.send(
			embed = (Embed(
					title       = "Success",
					description = (
						f"Successfully setup money unit donation of server to: {money_unit}"
					),
					color 	  = 0xf4f5c9,
					timestamp = datetime.now() 
				)
				.set_thumbnail(
					url = (
						interaction.user.avatar.url
						if interaction.user.avatar 
						else
						self.bot.user.avatar.url
						if self.bot.user and self.bot.user.avatar
						else None
					)
				)
			)
		)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DonationUnitSlash(bot = bot))