from discord.ext import commands
from core_utils.container import container_instance
from sql.donation_manager import DonationManager
from discord import app_commands, Member, Interaction
from core_utils.type_alias import DisableAllMentions, CanSendMessageChannel
from widgets.donation_add_widget import DonationAddWidget, DonationDataContext

_CSMC = CanSendMessageChannel
class DonationAddSlash(commands.Cog):
	_MIN_AMOUNT = 0
	_DAM        = DisableAllMentions

	def __init__(self, bot: commands.Bot) -> None:
		self.bot  = bot
		self.pool = container_instance.get_postgres_manager().pool

		assert self.pool is not None
		self.donation_manager = DonationManager(self.pool)

	@app_commands.command(
		name 		= "donation_add",
		description = "Add donation to user"
	)
	@app_commands.describe(
		user   = "User you want add",
		amount = "Amount"
	)
	@app_commands.default_permissions(administrator = True)
	@app_commands.checks.bot_has_permissions(administrator = True)
	@app_commands.checks.cooldown(rate = 1, per = 15, key = lambda i: i.user.id)
	async def donation_add(self, 
						interaction: Interaction, 
						user: Member, amount: float) -> None:
		if not interaction.guild:
			await interaction.response.send_message(
				content = (
					"Could not use this command in DM"
				),
				ephemeral = True
			)

			return
		
		if amount <= self._MIN_AMOUNT:
			await interaction.response.send_message(
				content = (
					f"Cannot set donation below `{self._MIN_AMOUNT}`"
				),
				ephemeral = True
			)

			return
		
		await interaction.response.defer()
		
		unit_money = await self.donation_manager.get_money_unit(
			guild_id = interaction.guild.id
		)
		channel_id = await self.donation_manager.get_log_channel(
			guild_id = interaction.guild.id 
		)
		webhook_message = await interaction.followup.send(
			f"Confirm to add: `{amount}` `{unit_money}` "
			f"to: **{user.name}**",
			wait 			 = True,
			allowed_mentions = self._DAM
		)

		await webhook_message.edit(
			view = DonationAddWidget(
				ctx = DonationDataContext(
					interaction 	= interaction,
					unit_money  	= unit_money,
					amount 			= amount,
					log_channel 	= channel_id,
					donator     	= user,
					webhook_message = webhook_message
				)
			)
		)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DonationAddSlash(bot = bot))