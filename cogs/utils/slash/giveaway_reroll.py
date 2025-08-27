from dataclasses import dataclass
from typing import Optional
from discord import (
	NotFound, app_commands, Interaction, TextChannel,
	Message, Embed
)
from discord.ui import View, Button
from discord.ext import commands
from datetime import datetime
from random import choice
from core_utils.type_alias import CanSendMessageChannel

@dataclass
class _GiveawayData:
	message: Message
	interaction: Interaction

class JumpToWidget(View):
	def __init__(self, url: str) -> None:
		super().__init__()
		self.url = url

		self.add_item(Button(
			label = "Jump to Giveaway",
			url = self.url
		))

class GiveawayRerollSlash(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		
	_FALLBACK_BOT_ID = [1099817714345840752, 1045600567633915975]
	_MIN_GWS_JOIN = 1
	_REACT_EMO = "🎉"

	def __edit_ended_to_embed(self, message: Message) -> Embed:
		embed = (Embed(
			title = "Giveaway has ended",
			description = message.embeds[0].description,
			color = message.embeds[0].color,
			timestamp = message.embeds[0].timestamp
		)
		.set_image(url = message.embeds[0].image.url)
		.set_thumbnail(url = message.embeds[0].thumbnail.url)
		.set_footer(text = message.embeds[0].footer.text))

		return embed

	async def __err_not_found_show(self, interaction: Interaction) -> None:
		await interaction.followup.send(content = (
			f"Giveaway in channel {(
				interaction.channel.mention
				if isinstance(interaction.channel, TextChannel)
				else 'unknown channel'
			)} not found, " \
			"please make sure this message ID is valid"
		), ephemeral = True)


	async def __fetch_and_reroll(self, gws_data: _GiveawayData) -> None:
		interaction = gws_data.interaction
		message = (
			gws_data.message 
			
		)

		if (
			message.author.id not in self._FALLBACK_BOT_ID 
			if not self.bot.user 
			else message.author.id != self.bot.user.id):
			await interaction.followup.send(
				content = "Giveaway is not started by bot",
				ephemeral = True
			)
			return
		
		reaction = next(
			(react for react in message.reactions 
					if str(react.emoji) == "🎉"
			), None
		)
		
		if (not reaction or reaction.count == self._MIN_GWS_JOIN):
			await interaction.followup.send(
				content = "No one entered giveaway, no need to reroll",
				ephemeral = True
			)
			return
		
		participants = [user async for user in reaction.users() if not user.bot]
		total_participants = len(participants)
		winner = choice(participants)
		win_rate = round(100 / total_participants)
		time_now = int(datetime.now().timestamp())

		await message.edit(embed = self.__edit_ended_to_embed(message = message))
		await message.reply(
			content = (
				f"* Giveaway with id `{message.id}` has ended\n" \
				f"* Winner: {winner.mention}\n" \
				f"* Win rate: `{win_rate}%`\n" \
				f"* End at: <t:{time_now}:R>"
			),
			view = JumpToWidget(message.jump_url)
		)
		await interaction.followup.send(content = (
			"* Successfully to reroll this giveaway\n" \
			f"* Giveaway ID: `{message.id}`"
		))

	@app_commands.command(
		name = "giveaway_reroll",
		description = "Reroll the giveaway"
	)
	@app_commands.describe(
		message_id = "Message ID",
		giveaway_channel = "Channel where the giveaway takes place"
	)
	@app_commands.checks.has_permissions(
		manage_channels = True
	)
	@app_commands.checks.bot_has_permissions(
		embed_links = True,
		read_message_history = True,
		send_messages = True
	)
	@app_commands.checks.cooldown(1, 15, key = lambda i: i.user.id)
	async def giveaway_reroll(
			self, interaction: Interaction,
			message_id: str, 
			giveaway_channel: Optional[CanSendMessageChannel] = None) -> None:
		if not interaction.guild:
			return

		await interaction.response.defer(ephemeral = True)
		if not giveaway_channel:
			if isinstance(interaction.channel, CanSendMessageChannel):
				current_channel = interaction.channel
				try:
					message = await current_channel.fetch_message(int(message_id))

				except NotFound:
					await self.__err_not_found_show(interaction = interaction)
					return

				except Exception:
					return
				
				gws_data = _GiveawayData(
					message = message, interaction = interaction
				)
				await self.__fetch_and_reroll(gws_data = gws_data)

			return

		try:
			message = await giveaway_channel.fetch_message(int(message_id))
	
		except NotFound:
			await self.__err_not_found_show(interaction = interaction)
			return

		except Exception:
			return
		
		gws_data = _GiveawayData(
			message = message, interaction = interaction
		)
		await self.__fetch_and_reroll(gws_data = gws_data)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(GiveawayRerollSlash(bot = bot))