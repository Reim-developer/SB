from discord.ext 		   import commands
from discord 			   import app_commands, Interaction, TextChannel
from sql.donation_manager  import DonationManager
from core_utils.container  import container_instance
from caches.donation_cache import DonationCache

class DonationLogSlash(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot   			= bot
		self.pool  			= container_instance.get_postgres_manager().pool
		self.redis 		    = container_instance.get_redis_manager().new_or_get()
		self.donation_cache = DonationCache(self.redis)

		assert self.pool is not None
		self.donation_manager = DonationManager(self.pool, self.donation_cache)

	@app_commands.command(
			name = "donation_set_log", 
			description = "Set donation log")
	@app_commands.describe(channel = "Log channel you want to set")
	@app_commands.checks.cooldown(rate = 1, per = 15, key = lambda i: i.user.id)
	@app_commands.default_permissions(administrator = True)
	@app_commands.checks.bot_has_permissions(administrator = True)
	async def donation_set_log(self, 
			interaction: Interaction, channel: TextChannel) -> None:
		if not interaction.guild:
			await interaction.response.send_message(
				"Could not use this command in DM",
				ephemeral = True
			)
			return

		await interaction.response.defer()
		await self.donation_manager.set_log_channel(
			guild_id   = interaction.guild.id,
			channel_id = channel.id
		)

		await interaction.followup.send(
			f"Successfully set donation log channel to: {channel.mention}"
		)
		
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DonationLogSlash(bot = bot))