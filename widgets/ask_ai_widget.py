from typing import List, Self
from discord import ButtonStyle, Interaction
from discord.ui import View, Button

class AskAIWidget(View):
	def __init__(self, pages: List[str], _interaction: Interaction):
		super().__init__(timeout = 180)
		self.__pages 		= pages 
		self.__current_page = 0
		self.__interaction  = _interaction

		self.__next_button: Button[Self]  = Button(
			label = "Next Page", style = ButtonStyle.gray
		)
		self.__prev_button: Button[Self]  = Button(
			label = "Prev Page", style = ButtonStyle.gray
		)

		self.__next_button.callback = self.__on_next_page
		self.__prev_button.callback = self.__on_prev_page

		self.add_item(self.__prev_button)
		self.add_item(self.__next_button)

		self.__update_buttons()

	def __update_buttons(self) -> None:
		self.__next_button.disabled = self.__current_page >= len(self.__pages) - 1
		self.__prev_button.disabled = self.__current_page <= 0

	async def __on_next_page(self, interaction: Interaction) -> None:
		if interaction.user.id != self.__interaction.user.id:
			await interaction.response.send_message(
				content   = (
					"You cannot interact with this "
					"button because you're not the command "
					"executor"
				),
				ephemeral = True
			)

			return 

		if self.__current_page < len(self.__pages) - 1:
			self.__current_page += 1
			self.__update_buttons()

			await interaction.response.edit_message(
				content = self.__pages[self.__current_page],
				view    = self
			)

		else:
			await interaction.response.defer()

	async def __on_prev_page(self, interaction: Interaction) -> None:
		if interaction.user.id != self.__interaction.user.id:
			await interaction.response.send_message(
				content   = (
					"You cannot interact with this "
					"button because you're not the command "
					"executor"
				),
				ephemeral = True
			)

			return 

		if self.__current_page > 0:
			self.__current_page -= 1
			self.__update_buttons()

			await interaction.response.edit_message(
				content = self.__pages[self.__current_page],
				view 	= self
			)

		else:
			await interaction.response.defer()

	async def on_timeout(self) -> None:
		for item in self.children:
			if isinstance(item, Button):
				item.disabled = True