from discord.ext import commands
from core_utils.container import container_instance
from sql.donation_manager import DonationManager, DonationData
from discord import app_commands, User, Member, Interaction, Embed
from core_utils.type_alias import DisableAllMentions, CanSendMessageChannel
from dataclasses import dataclass
from core_utils.time_utils import TimeUtils

@dataclass
class _DonationAddContext:
	channel_id:   int
	user: 	  User | Member
	added_amount: float
	interaction:  Interaction
	money_unit:   str 

_CSMC = CanSendMessageChannel
class DonationAddSlash(commands.Cog):
	_MIN_AMOUNT = 0
	_DAM        = DisableAllMentions

	def __init__(self, bot: commands.Bot) -> None:
		self.bot  = bot
		self.pool = container_instance.get_postgres_manager().pool

		assert self.pool is not None
		self.donation_manager = DonationManager(self.pool)

	async def __send_add_donation(self, ctx: _DonationAddContext) -> None:
		assert ctx.interaction.guild is not None # It's always not `None`

		channel = ctx.interaction.guild.get_channel(ctx.channel_id)
		if channel and isinstance(channel, _CSMC):
			await channel.send(embed = Embed(
				title       = "Add Donation Notification",
				description = (
					f"* By: {ctx.interaction.user} | `{ctx.interaction.id}`\n"
					f"* To: {ctx.user.name} | `{ctx.user.id}`\n"
					f"* At: <t:{TimeUtils.unix_time()}:R>\n"
					f"* Added Amount: `{ctx.added_amount}` `{ctx.money_unit}`"
				),
				color       = 0xb8c0cf
			).set_thumbnail(
				url = (
					ctx.interaction.user.avatar.url
					if ctx.interaction.user.avatar 
					else ctx.interaction.guild.icon.url 
					if ctx.interaction.guild.icon 
					else self.bot.user.avatar.url
					if self.bot.user and self.bot.user.avatar
					else None
				)
			))

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
						user: User | Member, amount: float) -> None:
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

		await self.donation_manager.add_donation(DonationData(
			guild_id = interaction.guild.id,
			user_id  = user.id,
			amount   = amount
		))
		money_unit = await self.donation_manager.get_money_unit(
			guild_id = interaction.guild.id
		)
		channel_id = await self.donation_manager.get_log_channel(
			guild_id = interaction.guild.id 
		)

		if channel_id:
			await self.__send_add_donation(_DonationAddContext(
				channel_id   = channel_id,
				interaction  = interaction,
				user 	     = user,
				added_amount = amount,
				money_unit   = money_unit 
			))

		await interaction.followup.send(
			f"* Successfully add `{amount}` `{money_unit}` to {user.display_name}",
			allowed_mentions = self._DAM
		)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DonationAddSlash(bot = bot))