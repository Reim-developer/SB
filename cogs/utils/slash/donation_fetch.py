from discord.ext 		   import commands
from discord 			   import app_commands, Interaction, User, Member
from sql.donation_manager  import DonationManager
from core_utils.container  import container_instance
from core_utils.type_alias import DisableAllMentions

class DonationFetchSlash(commands.Cog):
	_NO_DONATE_VALUE = 0
	_DAM 		     = DisableAllMentions

	def __init__(self, bot: commands.Bot) -> None:
		self.bot 	= bot
		self.__pool = container_instance.get_postgres_manager().pool

		assert self.__pool is not None
		self.__donation_manager = DonationManager(self.__pool)

	@app_commands.command(
		name 		= "donation_fetch",
		description = "Fetch donation value of user"
	)
	@app_commands.describe(
		user = "Member or user ID"
	)
	@app_commands.default_permissions(administrator = True)
	@app_commands.checks.cooldown(rate = 1, per = 15, key = lambda i: i.user.id)
	@app_commands.checks.bot_has_permissions(administrator = True)
	async def donation_fetch(self, 
						  interaction: Interaction, 
						  user: User | Member) -> None:
		if not interaction.guild:
			await interaction.response.send_message(
				content = (
					"Cannot use this command in DM"
				),
				ephemeral = True
			)

			return
		
		unit_money = await self.__donation_manager.get_money_unit(
			guild_id = interaction.guild.id
		)
		user_donation = await self.__donation_manager.get_user_donation(
			guild_id = interaction.guild.id,
			user_id  = user.id 
		)
		if user_donation == self._NO_DONATE_VALUE:
			await interaction.response.send_message(
				content = (
					f"This user: {user.name} is never donated"
				),
				ephemeral = True
			)
			return
		
		await interaction.response.send_message(
			content = (
				f"{user.name} donated `{user_donation:f}` **{unit_money}** "
				"to the server"
			),
			allowed_mentions = self._DAM
		)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DonationFetchSlash(bot = bot))