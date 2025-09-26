from discord.ui import (
	View, Button, button, Modal, TextInput
)
from discord import (
	ButtonStyle, Interaction, TextStyle, Embed, TextChannel,
	User, Member
)
from typing import Optional, Self
from datetime import datetime
from asyncio import sleep
from discord.ext import commands
from core_utils.container import container_instance
from core_utils.url import URLUtils
from sql.blacklist_manager import BlacklistManager, BlacklistResult
from core_utils.type_alias import DisableAllMentions

Bot = commands.AutoShardedBot | commands.Bot
Author = User | Member

class ReplyAnonymousWidget(Modal):
	_DAM 						   = DisableAllMentions
	reply_content: TextInput[Self] = TextInput(
		label = "Reply Confession (Anonymous)",
		placeholder = "Submit your reply content (Anonymous)",
		style = TextStyle.long,
		required = True,
		min_length = 1,
		max_length = 3500
	)
	image_url: TextInput[Self] = TextInput(
		label 		= "Image URL (Optional)",
		placeholder = "Submit Image URL...",
		style 	    = TextStyle.short,
		required    = False,
		max_length  = 250
	)

	def __init__(self, bot: Bot) -> None:
		super().__init__(title = "Anonymous Reply Confession")
		self.reply_content.callback = self.on_submit
		self.bot = bot
		self.LOG_CHANNEL = self.bot.get_channel(1057274847459295252)

	def __reply_embed(self, content: str, image_url: Optional[str]) -> Embed:
		embed = (Embed(
				title = "Anonymous Reply Confession",
				description = content,
				color = 0xbed0f7,
				timestamp = datetime.now()
			).set_image(
				url = image_url if image_url else None
			)
		)

		return embed
	
	async def __send_log(
			self, log_channel: TextChannel, 
			message: str, author: Author) -> None:
		time_now = int(datetime.now().timestamp())
		
		await log_channel.send(
			content = (
				f"* Message Content: {message}\n"
				f"* Message Image URL: {(
					self.image_url 
					if self.image_url else 'No Image'
				)}\n" 
				f"* Author ID: `{author.id}`\n"
				f"* Time: <t:{time_now}:R>"
			),
			allowed_mentions = self._DAM
		)

	async def on_submit(self, interaction: Interaction) -> None:
		content   = self.reply_content.value
		image_url = self.image_url.value

		if image_url and not URLUtils.valid_url(image_url):
			await interaction.response.send_message(
				content = (
					f"* Your image URL: `{image_url}` is not valid "
					"please try again"
				)
			)
			return 

		await interaction.response.send_message(
			embed = self.__reply_embed(
				content   = content,
				image_url = image_url
			),
			view = ReplyWidget(self.bot)
		)
		message = await interaction.original_response()
		if isinstance(self.LOG_CHANNEL, TextChannel):
			await self.__send_log(
				log_channel = self.LOG_CHANNEL,
				message = content,
				author = interaction.user
			)

		await sleep(0.5)
		await message.add_reaction("👍")
		await message.add_reaction("👎")
		await sleep(0.5)
		await message.create_thread(
			name = "What do you about this reply?",
			auto_archive_duration = 1440
		)

class PublicWidget(Modal):
	reply_content: TextInput[Self] = TextInput(
		label = "Reply Confession (Public)",
		placeholder = "Submit your reply content (Public)",
		style = TextStyle.long,
		required = True,
		min_length = 1,
		max_length = 3500
	)
	image_url: TextInput[Self] = TextInput(
		label 		= "Image URL (Optional)",
		placeholder = "Submit Image URL...",
		style 	    = TextStyle.short,
		required    = False,
		max_length  = 250
	)

	def __init__(self, bot: Bot) -> None:
		super().__init__(title = "Public Reply Confession")
		self.reply_content.callback = self.on_submit
		self.bot = bot

	def __reply_embed(self, 
				   content: str, image_url: Optional[str],
				   interaction: Interaction) -> Embed:
		author = interaction.user
		embed = (Embed(
				title = "Public Reply Confession",
				description = content,
				color = 0xfaafaa,
				timestamp = datetime.now()
			).set_image(
				url = image_url if image_url else None
			)
		)
		embed.set_footer(text = f"Reply by: {author.name}")
		embed.set_thumbnail(url = author.avatar.url if author.avatar else None)

		return embed

	async def on_submit(self, interaction: Interaction) -> None:
		content = self.reply_content.value
		image_url = self.image_url.value

		if image_url and not URLUtils.valid_url(image_url):
			await interaction.response.send_message(
				content = (
					f"* Your image URL: `{image_url}` is not valid "
					"please try again"
				)
			)
			return 


		await interaction.response.send_message(
			embed = self.__reply_embed(
				content 	= content, 
				image_url 	= image_url,
				interaction = interaction
			),
			view = ReplyWidget(bot = self.bot)
		)
		message = await interaction.original_response()

		await sleep(0.5)
		await message.add_reaction("👍")
		await message.add_reaction("👎")
		await sleep(0.5)
		await message.create_thread(
			name = "What do you about this reply?",
			auto_archive_duration = 1440
		)

class ReportWidget(Modal):
	report_reason: TextInput[Self] = TextInput(
		label = "Reason",
		placeholder = "What's wrong with this confession?",
		style = TextStyle.long,
		required = True,
		min_length = 1,
		max_length = 3500
	)
	report_msg_id: TextInput[Self] = TextInput(
		label = "Message ID",
		placeholder = "Message ID of that confession message",
		style = TextStyle.short,
		required = True,
		min_length = 10,
		max_length = 100
	)

	def __init__(self, bot: Bot) -> None:
		super().__init__(title = "Report Confession")
		self.bot = bot
		self.REPORT_CHANNEL = self.bot.get_channel(1408341510906318919)

	async def on_submit(self, interaction: Interaction) -> None:
		await interaction.response.defer(ephemeral = True)

		if isinstance(self.REPORT_CHANNEL, TextChannel):
			await self.REPORT_CHANNEL.send(content = (
				f"**__Report Notification__**\n" \
				f"* By: {interaction.user.name}\n" \
				f"* Reason: {self.report_reason.value}\n" \
				f"* ID Message/Confession: {self.report_msg_id}\n"
			))

		await interaction.followup.send(content = (
			f"Hello {interaction.user.name}, thank you for reporting!\n" \
			"Your complaint will be reviewed by us shortly and no one will " \
			"know you have made a complaint"
		), ephemeral = True)


class ReplyWidget(View):
	def __init__(self, bot: Bot) -> None:
		super().__init__(timeout = None)
		self.bot = bot

		self.__pool = container_instance.get_postgres_manager().pool
		assert self.__pool is not None
		self.__blacklist_manager = BlacklistManager(self.__pool)
		
	__ANONYMOUS_BUTTON_ID: str = "ANONYMOUS_BUTTON_ID"
	__PUBLIC_BUTTON_ID: str = "PUBLIC_BUTTON_ID"
	__REPORT_BUTTON_ID: str = "REPORT-BUTTON_ID"
		
	@button(
			label = "Anonymous Reply", 
			style = ButtonStyle.gray, 
			emoji = "<:private:1408309258638069781>",
			custom_id = __ANONYMOUS_BUTTON_ID)
	async def on_anonymous_reply(
			self, interaction: Interaction, 
			_: Button[Self]) -> None:
		
		user = interaction.user
		is_blacklist = self.__blacklist_manager.is_blacklisted(user.id)

		if await is_blacklist == BlacklistResult.BLACKLISTED:
			await interaction.response.send_message(
				content = (
					f"Hello, {interaction.user.name}\n" \
					"Sorry but you have been blacklisted, details " \
					"please join our support server to appeal\n" \
					"https://discord.gg/S9Z4uUmXbA"
				),
				ephemeral = True
			)
			return
		
		await interaction.response.send_modal(ReplyAnonymousWidget(self.bot))

	@button(
			label = "Public Reply",
			style = ButtonStyle.gray,
			emoji = "<:public:1408309805344358400>",
			custom_id = __PUBLIC_BUTTON_ID)
	async def on_public_reply(
			self, interaction: Interaction,
			_: Button[Self]) -> None:
		
		user = interaction.user
		is_blacklist = self.__blacklist_manager.is_blacklisted(user.id)

		if await is_blacklist == BlacklistResult.BLACKLISTED:
			await interaction.response.send_message(
				content = (
					f"Hello, {interaction.user.name}\n" \
					"Sorry but you have been blacklisted, details " \
					"please join our support server to appeal\n" \
					"https://discord.gg/S9Z4uUmXbA"
				),
				ephemeral = True
			)
			return
		
		await interaction.response.send_modal(PublicWidget(self.bot))
	
	@button(
			label = "Report",
			style = ButtonStyle.gray,
			emoji = "<:report:1408313874972934245>",
			custom_id = __REPORT_BUTTON_ID)
	async def on_report(
			self, interaction: Interaction,
			_: Button[Self]) -> None:
		
		await interaction.response.send_modal(ReportWidget(bot = self.bot))
