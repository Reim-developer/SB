from dataclasses 		   import dataclass
from discord.ext 		   import commands
from discord 			   import (
	TextChannel, Thread, app_commands, Interaction, Embed
)
from core_utils.container  import container_instance
from sql.donation_manager  import DonationManager
from datetime 		       import datetime 
from core_utils.time_utils import TimeUtils
from caches.donation_cache import DonationCache
from core_utils.type_alias import DisableAllMentions

@dataclass
class _UnitModifyContext:
	channel_id:  int
	interaction: Interaction
	money_unit:  str

class DonationUnitSlash(commands.Cog):
	_MIN_UNIT_LENGTH = 32
	_MAX_UNIT_COUNT  = 25
	_DAM 		     = DisableAllMentions

	def __init__(self, bot: commands.Bot) -> None:
		self.bot  = bot
		self.pool = container_instance.get_postgres_manager().pool
		self.redis 			= container_instance.get_redis_manager().new_or_get()
		self.donation_cache = DonationCache(redis = self.redis)

		assert self.pool is not None
		self.donation_manager = DonationManager(self.pool, self.donation_cache)

	async def __maxium_unit_count_reject(self, interaction: Interaction) -> None:
		await interaction.followup.send(
				content = (
					f"The number of units in the servers has reached "
					f"maxium of `{self._MAX_UNIT_COUNT}`.\n"
					"Please remove them and try again"
				)
			)
		
	async def __exists_unit_reject(self, interaction: Interaction, unit_name: str) -> None:
		await interaction.followup.send(
			content = (
				f"The unit: `{unit_name}` is already exists."
			),
			allowed_mentions = self._DAM
		)

	async def __maxium_characters_reject(self, interaction: Interaction) -> None:
		await interaction.response.send_message(
				f"Could not set money unit over `{self._MIN_UNIT_LENGTH}` characters",
			)

	async def __send_log_unit_modify(self, ctx: _UnitModifyContext) -> None:
		assert ctx.interaction.guild is not None # Interaction.guild will always not `None` here

		channel = ctx.interaction.guild.get_channel(ctx.channel_id)
		if channel and isinstance(channel, TextChannel | Thread):
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
		unit_name = "Money unit of donation"
	)
	@app_commands.checks.cooldown(rate = 1, per = 15, key = lambda i: i.user.id)
	@app_commands.checks.bot_has_permissions(administrator = True)
	@app_commands.default_permissions(administrator = True)
	async def donation_unit_set(self, 
							 interaction: Interaction, unit_name: str) -> None:
		if not interaction.guild:
			return 
		
		if len(unit_name) >= self._MIN_UNIT_LENGTH:
			await self.__maxium_characters_reject(interaction)
			return
		
		await interaction.response.defer()

		units = await self.donation_manager.get_unit_names(guild_id = interaction.guild.id)
		if len(units) >= self._MAX_UNIT_COUNT:
			await self.__maxium_unit_count_reject(interaction)
			return
		
		if unit_name in units:
			await self.__exists_unit_reject(interaction, unit_name)
			return

		await self.donation_manager.add_unit_name(
			guild_id   = interaction.guild.id,
			unit_name  = unit_name
		)

		channel_id = await self.donation_manager.get_log_channel(
			guild_id = interaction.guild.id
		)
		if channel_id:
			await self.__send_log_unit_modify(_UnitModifyContext(
				channel_id  = channel_id,
				interaction = interaction,
				money_unit  = unit_name
			))

		await interaction.followup.send(
			embed = (Embed(
					title       = "Success",
					description = (
						f"Successfully set unit name of donation for the "
						f"server to: {unit_name}"
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