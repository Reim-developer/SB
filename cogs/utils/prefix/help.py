from dataclasses import dataclass
from typing import Optional, Self, TypeAlias
from json_helper import emoji, prefix
from discord.ext import commands
from discord.ui import View, select, Select 
from discord import Embed, Interaction, SelectOption, Message 
from datetime import datetime
from collections import defaultdict
from datetime import datetime, timedelta

_Context: TypeAlias = commands.Context[commands.Bot]
_DefaultDict: TypeAlias = defaultdict[int, datetime]

@dataclass
class _HelpData:
	interaction: Interaction
	message: Message

class HelpSelectWidget(View):
	_SeOpt: TypeAlias = SelectOption 
	_SELECT_COOLDOWN: int = 10
	_UTILS_CMDS = "Utilities Commands"
	_CONFESSION_CMDS = "Confession Commands"
	_GIVEAWAYS_CMDS = "Giveaways Commands"
	_ANIME_CMDS = "Anime Commands"

	def __init__(self) -> None:
		super().__init__(timeout = 60)
		self.message: Optional[Message] = None
		self.ctx: Optional[_Context] = None
		self.cooldowns: _DefaultDict = defaultdict(lambda: datetime.min)

		self.utils_emo = emoji("UTILS")
		self.aliases_emo= emoji("ALIASES")
		self.dot_bottom_emo = emoji("DOT_BOTTOM")
		self.prefix_emo = emoji("PREFIX")
		self.separator_emo = emoji("SEPARATOR")
		self.slash_emo = emoji("SLASH")
		self.anime_emo = emoji("ANIME")
		self.confession_emo = emoji("CONFESSION")

		self.bot_prefix = prefix()

	async def __show_utils_help(self, help_data: _HelpData) -> None:
		interaction = help_data.interaction
		current_message = help_data.message

		embed = (Embed (
				description = (
					f"{self.utils_emo} **{self._UTILS_CMDS}**\n" \
					
					f"*	{self.prefix_emo} `{self.bot_prefix}` avatar\n" \
					f"* {self.aliases_emo} Aliases: [`av`, `avt`]\n" \
					f"{self.dot_bottom_emo} Show your avatar or another user avatar.\n" \
					
					f"{self.separator_emo}\n" \
					
					f"*	{self.prefix_emo} `{self.bot_prefix}` invite\n" \
					f"* {self.aliases_emo} Aliases: [`inv`, `invit`]\n" \
					f"{self.dot_bottom_emo} Show bot invite URL & support server.\n" \
					
					f"{self.separator_emo}\n" \
					
					f"* {self.prefix_emo} `{self.bot_prefix}` membercount\n" \
					f"* {self.aliases_emo} Aliases: [`mc`]\n" \
					f"{self.dot_bottom_emo} Show the server member count.\n"

					f"{self.separator_emo}\n" \
					
					f"* {self.slash_emo} `embed_builder`\n" \
					f"* {self.aliases_emo} Aliases: `None`\n" \
					f"{self.dot_bottom_emo} Build & send customize embed."
				),
				timestamp = datetime.now(),
				color = 0xf2e2c9
			).set_thumbnail(
				url = interaction.user.avatar.url
				if interaction.user.avatar else None
			)
		)
		await current_message.edit(embed = embed)

	
	async def __show_giveaways_help(self, help_data: _HelpData) -> None:
		interaction = help_data.interaction
		current_message = help_data.message

		embed = (Embed (
				description = (
					f"🎉 **{self._GIVEAWAYS_CMDS}**\n" \

					f"* {self.slash_emo} `giveaway_create`\n" \
					f"* {self.aliases_emo} Aliases: `None`\n" \
					f"{self.dot_bottom_emo} Create the giveaway\n" \
					
					f"{self.separator_emo}\n" \
					
					f"* {self.slash_emo} `giveaway_reroll`\n" \
					f"* {self.aliases_emo} Aliases: `None`\n" \
					f'{self.dot_bottom_emo} Reroll the giveaway\n' 
				),
				timestamp = datetime.now(),
				color = 0xf2e2c9
			).set_thumbnail(
				url = interaction.user.avatar.url
				if interaction.user.avatar else None
			)
		)
		await current_message.edit(embed = embed)

	async def __show_confession_help(self, help_data: _HelpData) -> None:
		interaction = help_data.interaction
		current_message = help_data.message

		embed = (Embed (
				description = (
					f"{self.confession_emo} **{self._CONFESSION_CMDS}**\n" \

					f"* {self.slash_emo} `/set_confession`\n" \
					f"* {self.aliases_emo} Aliases: `None`\n" \
					f"{self.dot_bottom_emo} Setup your confession channel\n" \
					
					f"{self.separator_emo}\n" \
					
					f"* {self.slash_emo} `/confession`\n" \
					f"* {self.aliases_emo} Aliases: `None`\n" \
					f"{self.dot_bottom_emo} Send your message to confession channel\n" \
				),
				timestamp = datetime.now(),
				color = 0xf2e2c9
			).set_thumbnail(
				url = interaction.user.avatar.url
				if interaction.user.avatar else None
			)
		)
		await current_message.edit(embed = embed)

	async def __show_anime_help(self, help_data: _HelpData) -> None:
		interaction = help_data.interaction
		current_message = help_data.message

		embed = (Embed (
				description = (
					f"{self.anime_emo} **{self._ANIME_CMDS}**\n" \

					f"* {self.slash_emo} `my_animelist_info`\n" \
					f"* {self.aliases_emo} Aliases: `None`\n" \
					f"{self.dot_bottom_emo} Show anime information with `MyAnimeList` ID\n" \
				),
				timestamp = datetime.now(),
				color = 0xf2e2c9
			).set_thumbnail(
				url = interaction.user.avatar.url
				if interaction.user.avatar else None
			)
		)
		await current_message.edit(embed = embed)

	async def __cooldown_warnings(
			self, interaction: Interaction,
			remaining_time: float
			) -> None:

		await interaction.followup.send(
			content = (
				f"{interaction.user.name}, please wait: <t:{int(remaining_time)}:R> " \
				"for use this command again"
			),
			ephemeral = True
		)

	@select(
		placeholder = "SB Discord Bot Help",
		min_values =  1,
		max_values = 1,
		options = [
			_SeOpt(
				label = f"{_UTILS_CMDS}", 
				description = "Useful Guide to Utilities Commands"
			),
			_SeOpt(
				label = f"{_GIVEAWAYS_CMDS}",
				description = "Useful Guide to Giveaways Commands"
			),
			_SeOpt(
				label = f"{_CONFESSION_CMDS}",
				description = "Useful Guide to Confession Commands"
			),
			_SeOpt(
				label = f"{_ANIME_CMDS}",
				description = "Useful Guide to Anime Commands"
			)
		] 
	)
	async def select_callback(self,  
					interaction: Interaction, 
					select: Select[Self]) -> None:
		await interaction.response.defer(ephemeral = True)
		author = interaction.user
		last_used = self.cooldowns[author.id]
		now = datetime.now()
		select_cooldown_time = timedelta(seconds = self._SELECT_COOLDOWN)

		if now - last_used < select_cooldown_time:
			remaining_time = (last_used + select_cooldown_time).timestamp()

			await self.__cooldown_warnings(
				interaction = interaction,
				remaining_time = remaining_time
			)

			return 

		if self.ctx and self.ctx.author.id != author.id:
			await interaction.followup.send(
				content = (
					"This command is not executed by you, it's not selectable"
				), 
				ephemeral = True
			)
			return

		if interaction.message and self.message:
			self.cooldowns[author.id] = now
			select_value = select.values[0]

			help_data = _HelpData(
				message = self.message,
				interaction = interaction
			)

			match select_value:
				case self._UTILS_CMDS:
					await self.__show_utils_help(help_data = help_data)

				case self._CONFESSION_CMDS:
					await self.__show_confession_help(help_data = help_data)

				case self._GIVEAWAYS_CMDS:
					await self.__show_giveaways_help(help_data = help_data)

				case self._ANIME_CMDS:
					await self.__show_anime_help(help_data = help_data)

				case _:
					...

	async def on_timeout(self) -> None:
		for item in self.children:
			if isinstance(item, Select):
				item.disabled = True

		if self.message:
			try:
				await self.message.edit(content = "This message is expired", view = None)

			except:
				... # Ignore some exception here. The message may have deleted before.

class HelpPrefix(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	@commands.command()
	@commands.cooldown(1, 15, commands.BucketType.user)
	async def help(
		self, 
		ctx: commands.Context[commands.Bot]) -> None:

		if not ctx.guild:
			return

		view = HelpSelectWidget()
		view.ctx = ctx

		message = await ctx.channel.send(view = view)
		view.message = message

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(HelpPrefix(bot = bot))