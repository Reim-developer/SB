from discord.ext                   import commands
from core_utils.container          import container_instance
from sql.donation_manager          import DonationManager
from discord                       import app_commands, Interaction, Embed
from datetime 			   		   import datetime
from core_utils.number_fmt         import Number
from caches.donation_cache 		   import DonationCache
from core_utils.autocomplete_slash import AutoComplete

class DonationGetSlash(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot  = bot
		self.pool = container_instance.get_postgres_manager().pool
		self.redis 			= container_instance.get_redis_manager().new_or_get()
		self.donation_cache = DonationCache(redis = self.redis)

		assert self.pool is not None
		self.donation_manager = DonationManager(self.pool, self.donation_cache)
		self.auto_complete    = AutoComplete(self.donation_manager)
		self.my_donation.autocomplete("unit_name")(self.auto_complete.unit_autocomplete)

	@app_commands.command(
		name        = "my_donation",
		description = "Show your donation"
	)
	@app_commands.describe(
		unit_name = "Name of unit you want to show",
	)
	@app_commands.checks.bot_has_permissions(administrator = True)
	async def my_donation(self, interaction: Interaction, unit_name: str) -> None:
		if not interaction.guild:
			await interaction.response.send_message(
				"Could not use this command in DM"
			)
			return 
		
		await interaction.response.defer()

		money = await self.donation_manager.get_user_donation(
			guild_id  = interaction.guild.id,
			user_id   = interaction.user.id,
			unit_name = unit_name
		)

		await interaction.followup.send(embed = Embed(
			title = "Donation Stats",
			description = (
				f"* You have now donated `{Number.fmt_donation(money)}` {unit_name} to the "
				f"{interaction.guild.name}"
			),
			color     = 0xdfebbc,
			timestamp = datetime.now()
		).set_thumbnail(
			url = (
				interaction.user.avatar.url
				if interaction.user.avatar else
				self.bot.user.avatar.url
				if self.bot.user and self.bot.user.avatar else None
			)
		))

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DonationGetSlash(bot = bot))