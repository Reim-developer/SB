from typing 	 import Optional, Self
from discord.ui  import View, Button
from discord 	 import (
	ButtonStyle, Interaction, Embed, 
	Member, TextChannel, Thread, WebhookMessage
)
from dataclasses 		   import dataclass
from core_utils.container  import container_instance
from sql.donation_manager  import DonationManager, DonationData
from core_utils.type_alias import CanSendMessageChannel
from core_utils.time_utils import TimeUtils
from datetime 			   import datetime
from caches.donation_cache import DonationCache

@dataclass
class DonationDataContext:
	interaction: 	 Interaction
	unit_name:  	 str
	amount: 	 	 int | float
	log_channel: 	 Optional[int]
	donator: 	 	 Member
	webhook_message: WebhookMessage 

class DonationAddWidget(View):
	_CSMC = CanSendMessageChannel
	def __init__(self, ctx: DonationDataContext) -> None:
		super().__init__(timeout = 30)
		self.__ctx 	 	    = ctx
		self.__interaction  = self.__ctx.interaction
		self.__pool 	    = container_instance.get_postgres_manager().pool
		self.redis 			= container_instance.get_redis_manager().new_or_get()
		self.donation_cache = DonationCache(redis = self.redis)

		assert self.__pool is not None
		self.__donation_manager = DonationManager(self.__pool, self.donation_cache)

		self.__confirm_button: Button[Self] = Button(
			label = "Confirm", 
			style = ButtonStyle.gray
		)
		self.__cancel_button: Button[Self] = Button(
			label = "Cancel",
			style = ButtonStyle.gray
		)
		
		self.__confirm_button.callback = self.__on_confirm
		self.__cancel_button.callback  = self.__on_cancel
		self.add_item(self.__confirm_button)
		self.add_item(self.__cancel_button)

	async def __send_add_donation(self, 
							   interaction: Interaction,
							   log_channel: int) -> None:
		assert interaction.guild is not None # It's always not `None`

		channel = interaction.guild.get_channel(log_channel)

		if channel and isinstance(channel, TextChannel | Thread):
			await channel.send(embed = Embed(
				title       = "Add Donation Notification",
				description = (
					f"* By: {interaction.user.name} | `{interaction.user.id}`\n"
					f"* To: {self.__ctx.donator.name} | `{self.__ctx.donator.id}`\n"
					f"* At: <t:{TimeUtils.unix_time()}:R>\n"
					f"* Added Amount: `{self.__ctx.amount}` `{self.__ctx.unit_name}`"
				),
				color       = 0xb8c0cf
			).set_thumbnail(
				url = (
					interaction.user.avatar.url
					if interaction.user.avatar 
					else interaction.guild.icon.url 
					if interaction.guild.icon 
					else None
				)
			))


	async def __add_donate(self, interaction: Interaction) -> None:
		assert interaction.guild is not None

		await self.__donation_manager.add_donation(DonationData(
			guild_id  = interaction.guild.id,
			user_id   = self.__ctx.donator.id,
			unit_name = self.__ctx.unit_name,
			amount    = self.__ctx.amount
		))
		channel_id = await self.__donation_manager.get_log_channel(
			guild_id = interaction.guild.id 
		)

		if channel_id:
			await self.__send_add_donation(
				interaction = interaction,
				log_channel = channel_id
			)

	async def __on_confirm(self, interaction: Interaction) -> None:
		if self.__interaction.user.id != interaction.user.id:
			await interaction.response.send_message(
				content   = (
					"You do not have permission to execute this"
				),
				ephemeral = True
			)
			return
		
		await interaction.response.defer()
		await self.__add_donate(interaction = interaction)
		message  = self.__ctx.webhook_message

		await message.edit(
			content = None,
			embed = Embed(
				description =  ( 
					f"Successfully added "
					f"`{self.__ctx.amount}` `{self.__ctx.unit_name}` " 
					f"to: **{self.__ctx.donator.name}**"
				),
				color 	  = 0xe4fcd2,
				timestamp = datetime.now()
			).set_thumbnail(
				url = (
					self.__ctx.donator.avatar.url
					if self.__ctx.donator.avatar
					else interaction.user.avatar.url
					if interaction.user.avatar else None
				)
			),
			view = None
		)
	
	async def __on_cancel(self, interaction: Interaction) -> None:
		if self.__interaction.user.id != interaction.user.id:
			await interaction.response.send_message(
				content   = (
					"You do not have permission to execute this"
				),
				ephemeral = True
			)
			return
		
		await interaction.response.defer()
		message = self.__ctx.webhook_message

		await message.edit(
			content = None,
			view 	= None,
			embed = Embed(
				description = f"Canceled add donation to: **{self.__ctx.donator.name}**",
				color 		= 0xcfcfcf,
				timestamp   = datetime.now()
			)
		)

	async def on_timeout(self) -> None:
		message = self.__ctx.webhook_message
		if not message.components:
			await message.edit(
				content = (
					f"* The transaction session with ID `{message.id}` "
					f"has expired at: <t:{TimeUtils.unix_time()}:R>"
				),
				view    = None
			)