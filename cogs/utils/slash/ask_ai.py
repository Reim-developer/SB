from typing import List
from discord.ext import commands
from discord import app_commands, Interaction 
from core_utils.config import ConfigUtils
from api.google_gemini import GoogleGeminiAPI
from core_utils.type_alias import DisableAllMentions
from widgets.ask_ai_widget import AskAIWidget

class AskAISlash(commands.Cog):
	_DAM 			 = DisableAllMentions
	_MAX_PAGE_LENGTH = 2000

	def __init__(self, bot: commands.Bot) -> None:
		self.bot 		     = bot
		self.__google_gemini = GoogleGeminiAPI(ConfigUtils.gemini_api_keys())

	def __split_answer(self, answer: str) -> List[str]:
		if len(answer) <= self._MAX_PAGE_LENGTH:
			return [answer]
		
		words 		 	 = answer.split(" ")
		pages: List[str] = []
		current_page     = ""

		for word in words:
			if len(current_page) + len(word) + 1 <= self._MAX_PAGE_LENGTH:
				if current_page:
					current_page += " " + word
				
				else:
					current_page += " " + word

			else:
				pages.append(current_page)
				current_page = word
		
		if current_page:
			pages.append(current_page)

		final_pages: List[str] = []
		for page in pages:
			while len(page) > self._MAX_PAGE_LENGTH:
				final_pages.append(page[:self._MAX_PAGE_LENGTH])
				page = page[self._MAX_PAGE_LENGTH:]

			final_pages.append(page)

		return final_pages
		
	@app_commands.command(
		name 		= "study_ask",
		description = "Ask AI for your learning purposes"
	)
	@app_commands.describe(
		question = "Your question"
	)
	@app_commands.checks.bot_has_permissions(administrator = True)
	@app_commands.checks.cooldown(rate = 1, per = 15, key = lambda i: i.user.id)
	async def study_ask(
		self, interaction: Interaction, question: str) -> None:
		if not interaction.guild:
			await interaction.response.send_message(
				content = (
					"Could not use this command in DM"
				)
			)
			return
		
		await interaction.response.defer()
		answer = self.__google_gemini.response(question = question)

		pages = self.__split_answer(answer = answer)

		await interaction.followup.send(
			content = pages[0],
			allowed_mentions = self._DAM,
			view 			 = AskAIWidget(
				pages 		 = pages,
				_interaction = interaction
			)
		)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(AskAISlash(bot = bot))