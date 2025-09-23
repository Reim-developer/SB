from dataclasses import dataclass, fields
from discord import (
	Interaction, TextStyle, Embed, ButtonStyle,
	WebhookMessage
)
from discord.ext import commands
from discord.ui import Modal, TextInput, View, button, Button
from discord.ui.text_input import V
from typing import (
	Callable, List, LiteralString, Optional, 
	Self, Tuple, TypeAlias
)
from re import match as regex_match
from core_utils.type_alias import CanSendMessageChannel

_T_INPUT: TypeAlias = TextInput[V]
_T_S: TypeAlias = TextStyle
_E: TypeAlias = Embed
_WARNING_RESULT = Tuple[List[str], int]
_ERR_RESULT = Tuple[List[str], int]
_CHECKS: TypeAlias = List[Tuple[bool, Callable[[], str]]]
_LIMIT_LENGTH: int = 6000
_CSMC = CanSendMessageChannel
_NIL_STR: LiteralString = ""

def _is_valid_hex(hex: str) -> bool:
	pattern = r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"

	return bool(regex_match(pattern = pattern, string = hex))

def _fmt_color(hex: str) -> Optional[int]:
	_BASE_INDEX = 16
	if not _is_valid_hex(hex = hex):
		return None
	
	if hex.startswith("#"):
		return int(hex[1:], _BASE_INDEX)
	
	return int(hex, _BASE_INDEX)

@dataclass
class ImageData:
	image: Optional[str]
	thumbnail: Optional[str]
	footer_icon: Optional[str]
	author_icon: Optional[str]

@dataclass
class _EmbedData:
	title: Optional[str]
	description: str
	color: Optional[int]
	footer_text: Optional[str]
	author_text: Optional[str]
	image_data: ImageData

@dataclass
class _BuilderOptionsData:
	embed_data: _EmbedData
	message: WebhookMessage
	bot: commands.Bot

# class _ImageBuilderOptions(Modal):
# 	def __init__(self) -> None: 
# 		super().__init__(title = "Edit Embed Image")

# 	image_build: _T_INPUT[Self] = TextInput(
# 		label 	   = "Embed Image URL",
# 		style 	   = _T_S.short,
# 		max_length = 256,
# 		required   = False
# 	)

# 	def embed_image_url(self, image_data: ImageData) -> ImageData:
# 		return image_data
	
class _BuilderOptions(View):
	_b = button
	_B_S = ButtonStyle
	_E = _EmbedData
	_B_O_D = _BuilderOptionsData

	def __init__(
			self, builder_data: _B_O_D,
			image_data: ImageData) -> None:
		super().__init__()
		self.embed_data = builder_data.embed_data
		self.message = builder_data.message
		self.bot = builder_data.bot
		self.image_data = image_data

	@_b(
		label = "Edit Embed Content",
		emoji = "<:edit:1413072289280299120>",
		style = _B_S.gray
	)
	async def on_content_edit(
			self, interaction: Interaction,
			_: Button[Self]) -> None:
		await interaction.response.send_modal(
			EmbedBuilderWidget(bot = self.bot, image_data = self.image_data)
			.set_default_modal(self.embed_data)
		)
		await self.message.delete()

	@_b(
		label = "Edit Embed Image",
		emoji = "<:edit:1413072289280299120>",
		style = _B_S.gray
	)
	async def on_image_edit(
			self, interacction: Interaction,
			_: Button[Self]) -> None: ...
		

	@_b(
		label = "Send Embed",
		emoji = "<:Embed:1413072146334486540>",
		style = _B_S.success,
	)
	async def on_send(
			self, interaction: Interaction,
			_: Button[Self]) -> None:
		
		current_channel = interaction.channel
		if isinstance(current_channel, _CSMC):
			embed_title 	  = (self.embed_data.title) \
				if self.embed_data.title else None
			
			embed_description = self.embed_data.description
			embed_color 	  = self.embed_data.color
			footer_text 	  = self.embed_data.footer_text
			author_text 	  = (self.embed_data.author_text) \
				if self.embed_data.author_text else _NIL_STR

			await current_channel.send(
				embed = (
					Embed(
						title 		= embed_title,
						description = embed_description,
						color 		= embed_color,
					)
					.set_footer(
						text 	 = footer_text,
						icon_url = (
							self.image_data.footer_icon
							if self.image_data.footer_icon
							else None
						)
					)
					.set_author(
						name 	 = author_text,
						icon_url = (
							self.image_data.author_icon
							if self.image_data.author_icon 
							else None
						)				
					)
					.set_image(url = (
						self.image_data.image
						if self.image_data.image
						else None
					)
				).set_thumbnail(
					url = (
						self.image_data.thumbnail
						if self.image_data.thumbnail
						else None
					)
				)
			))

			await interaction.response.send_message(
				content = (
					f"Successfully send message to: {current_channel.mention}!"
				),
				ephemeral = True
			)
			await self.message.delete()
			
class EmbedBuilderWidget(Modal):
	title_build: _T_INPUT[Self] = TextInput(
		label = "Embed title (Optional)",
		style = _T_S.short,
		placeholder = "...",
		max_length = 256,
		required = False
	)
	description_build: _T_INPUT[Self] = TextInput(
		label = "Embed Description (Required)",
		style = _T_S.paragraph,
		placeholder = "...",
		min_length = 1,
		max_length = 4000,
		required = True
	)
	color_build: _T_INPUT[Self] = TextInput(
		label = "Embed HEX Color (Optional)",
		placeholder = "...",
		style = _T_S.short,
		max_length = 20,
		required = False
	)
	footer_text_build: _T_INPUT[Self] = TextInput(
		label 		= "Embed Footer (Optional)",
		placeholder = "...",
		style 		= _T_S.paragraph,
		max_length  = 2048,
		required 	= False
	)
	author_text_build: _T_INPUT[Self] = TextInput(
		label 		= "Embed Author (Optional)",
		placeholder = "...",
		style 		= _T_S.short,
		max_length 	= 256,
		required 	= False
	)

	def __init__(
			self, bot: commands.Bot,
			image_data: ImageData) -> None:
		super().__init__(title = "Setup Embed")
		self.bot = bot
		self.image_data = image_data

	def __generate_warnings(self, embed_data: _EmbedData) -> _WARNING_RESULT:
		warnings_list = [
			f"* **Embed field `{field.name}` is not provided/or not valid.**"
			for field in fields(embed_data)
			if not getattr(embed_data, field.name)
		]

		return warnings_list, len(warnings_list)
	
	def __generate_errors(self) -> _ERR_RESULT:
			TITLE_LENGTH       = len(self.title_build.value)
			DESCRIPTION_LENGTH = len(self.description_build.value)
			FOOTER_TEXT_LENGTH = len(self.footer_text_build.value)
			AUTHOR_TEXT_LENGTH = len(self.author_text_build.value)
		
			checks: _CHECKS = [
				(
					TITLE_LENGTH +
					DESCRIPTION_LENGTH +
					AUTHOR_TEXT_LENGTH +
					FOOTER_TEXT_LENGTH > _LIMIT_LENGTH,
					lambda: (
						"* **Your embed cannot be sent because it " \
						f"exceeds Discord's {_LIMIT_LENGTH} character limit.**\n" \
						"* **Traceback:**\n" 
						f"* Title Length: `{TITLE_LENGTH}` character(s)\n" \
						f"* Description Length: `{DESCRIPTION_LENGTH}` characters(s)\n" \
						f"* Footer Text Length: `{FOOTER_TEXT_LENGTH}` characters(s)"
					)
				),
				(
					bool(self.color_build.value and not _is_valid_hex(self.color_build.value)),
					lambda: (
						"* Embed color does not exists, it only accepts HEX color format\n" \
						f"* Your embed color is: `{self.color_build.value}`\n"
					)
				),
		]

			errors = [msg_fn() for condition, msg_fn in checks if condition]
			return errors, len(errors)
	
	def set_default_modal(self, embed_data: _EmbedData) -> Self:
		self.title_build.default 	   = embed_data.title
		self.description_build.default = embed_data.description
		self.color_build.default       = str(embed_data.color) if embed_data.color else None
		self.author_text_build.default = embed_data.author_text
		self.footer_text_build.default = embed_data.footer_text

		return self

	async def on_submit(self, interaction: Interaction) -> None:
		title: Optional[str] = (
			self.title_build.value 
		) if self.title_build.value else None
		color: Optional[int] = _fmt_color(self.color_build.value)
		description: str = self.description_build.value
		footer_text: Optional[str] = (
			self.footer_text_build.value 
			if self.footer_text_build.value 
			else None
		)
		author_text: Optional[str] = (
			self.author_text_build.value
			if self.author_text_build.value
			else None
		)

		embed_data = _EmbedData(
			title 		= title, 		
			description = description,
			color 		= color, 		
			footer_text = footer_text,
			author_text = author_text,
			image_data	= self.image_data 
		)
		
		warnings_reason, warning_count = self.__generate_warnings(
			embed_data = embed_data
		)
		error_msg, err_count = self.__generate_errors()
		error = "\n".join(error_msg)
		await interaction.response.defer(
			ephemeral = True
		)
		if err_count:
			await interaction.followup.send(
				content   = error,
				ephemeral = True
			)
			return

		warn = "\n".join(warnings_reason)

		message = await interaction.followup.send(
			content = (
				"**__Information:__**\n" \
				f"{(
					"No warnings generated\n" 
					if warning_count <= 0 
					else
					f"* {warning_count} warnings generated\n" \
					"**Warnings Reason:**\n" \
					f"{warn}\n\n" \
					"* No errors generated\n\n"
					if err_count <= 0
					else "" # Auto-handling in otherwise case.
				)}" \
				"**__Preview:__**\n"
			),
			embed = (_E(
					title 		= title if title else _NIL_STR,
					description = description,
					color 		= color if color else None,
				)
				.set_author(
					name 	 = self.author_text_build 
						if self.author_text_build else _NIL_STR,

					icon_url = self.image_data.author_icon
						if self.image_data.author_icon else None 
				)
				.set_footer(
					text 	 = footer_text if footer_text else None,
					icon_url = (
						self.image_data.footer_icon
						if self.image_data.footer_icon 
						else None
					)
				)
				.set_image(
					url = (
						self.image_data.image
						if self.image_data.image
						else None
					)
				)
				.set_thumbnail(
					url = (
						self.image_data.thumbnail
						if self.image_data.thumbnail
						else None
					)
				)
			),
			ephemeral = True,
			wait 	  =  True
		)
		
		await message.edit(view = _BuilderOptions(
			_BuilderOptionsData(
				embed_data = embed_data,
				message = message,
				bot = self.bot
			), self.image_data)
		)
