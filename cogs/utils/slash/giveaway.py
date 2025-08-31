from dataclasses import dataclass
from typing import Optional, TypeAlias
from discord import (
	Role, app_commands, Interaction, Embed,
	Message
)
from discord.ext import commands
from core_utils.time_utils import TimeUtils
from datetime import datetime
from time import time
from asyncio import sleep
from sql.sql_manager import SQLiteManager
from core_utils.giveaway_timer import (
	GiveawayData, GiveawayTimer, TimerData
)
from urllib.parse import urlparse
from core_utils.type_alias import CanSendMessageChannel

_MAX_TITLE = 210
_MAX_DESCRIPTION = 4000
_CSMC: TypeAlias = CanSendMessageChannel
@dataclass
class _GiveawayData:
	prize: str
	time: int
	interaction: Interaction
	image_url: Optional[str]
	mention_role: Optional[Role]

class GiveawaysSlash(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.sqlite_manager = SQLiteManager("database/database.db")
		self.__giveaway_timer = GiveawayTimer(TimerData(
			bot = self.bot,
			sqlite_manager = self.sqlite_manager
		))

	def __valid_url(self, url: str) -> bool:
		try:
			result = urlparse(url = url)

			return all([result.scheme, result.netloc])
		
		except:
			return False

	def __invalid_time(self, wrong_time: str) -> Embed:
		embed = Embed(
			title = f"Invalid time: {(
				f'{wrong_time[0:100]} and {len(wrong_time)} character(s)' 
				if len(wrong_time) >= _MAX_TITLE
				else wrong_time
			)}",
			description =  (
				"**Please use according to our time standards:**\n" \
				"* Year: `y`\n" \
				"* Week: `w`\n" \
				"* Day: `d`\n" \
				"* Hour: `h`\n" \
				"* Second: `s`\n"
			),
			color = 0xbeface,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(
			url = self.bot.user.avatar.url
			if self.bot.user and self.bot.user.avatar
			else None
		)

		return embed
	
	async def __add_gws_id(self, message: Message) -> None:
		embed = Embed(
			title = message.embeds[0].title,
			description = message.embeds[0].description,
			color = message.embeds[0].color,
			timestamp = message.embeds[0].timestamp
		).set_footer(
			text = f"Giveaway ID: {message.id}"
		).set_thumbnail(
			url = message.embeds[0].thumbnail.url
		).set_image(url = message.embeds[0].image.url)

		await message.edit(embed = embed)
	
	async def __giveaway_embed_send(self, gws_data: _GiveawayData) -> Optional[Message]:
		interaction = gws_data.interaction
		end_at = gws_data.time
		prize = gws_data.prize
		end_at_unix_time = int(time() + end_at)
		ping_message = gws_data.mention_role

		author = interaction.user	
		embed = Embed(
			title = f"🎉 {author.name}'s Giveaway",
			description = (
				"**__Prize:__**\n" \
				f"{(
					f'{prize[0:4000]} and {len(prize)} character(s)...'
					if  len(prize) >= _MAX_DESCRIPTION else prize
				)}\n\n" \
				f"**__End At:__** <t:{end_at_unix_time}>"
			),
			timestamp = datetime.now(),
			color = 0xf7d6cb
		)
		embed.set_thumbnail(
			url =  author.avatar.url
			if author.avatar else None
		)
		if gws_data.image_url and self.__valid_url(url = gws_data.image_url):
			embed.set_image(url = gws_data.image_url)

		text_channel = interaction.channel
		if isinstance(text_channel, _CSMC):
			message = await text_channel.send(
				content = (
					f"{ping_message.mention}" 
					if ping_message else ''
				),
				embed = embed
			)

			return message
		
		return None
	
	@app_commands.command(
		name = "giveaway_create",
		description = "Create a giveaway"
	)
	@app_commands.describe(
		prize = "Your giveaway prize",
		end_at = "How long does the giveaway last?",
		image_url = "Your giveaway image (URL)",
		mention_role = "The role you want to mention"
	)
	@app_commands.checks.has_permissions(
			manage_channels = True, 
			mention_everyone = True)
	@app_commands.checks.bot_has_permissions(
			embed_links = True,
			mention_everyone = True,
			send_messages = True,
			read_message_history = True 
	)
	@app_commands.checks.cooldown(1, 10, key = lambda i: i.user.id)
	async def giveaway_create(
			self, interaction: Interaction,
			prize: str, end_at: str, image_url: Optional[str] = None,
			mention_role: Optional[Role] = None) -> None:
		if not interaction.guild:
			return
		
		await interaction.response.defer(ephemeral = True)
		time_format = TimeUtils.parse(end_at)
		if not time_format:
			await interaction.followup.send(
				embed = self.__invalid_time(wrong_time= end_at
				),
				ephemeral = True
			)
			return
		
		gws_data = _GiveawayData(
			prize = prize,
			time = time_format,
			interaction = interaction,
			image_url = image_url,
			mention_role = mention_role,
		)
		current_channel = interaction.channel
		if isinstance(current_channel, _CSMC):
			message = await self.__giveaway_embed_send(gws_data = gws_data)
			if message:
				giveaway_id = message.id
				time_end_at = int(time() + time_format)

				await self.__add_gws_id(message = message)
				await interaction.followup.send(
					content = f"Successfully create giveaway. Your giveaway ID: {giveaway_id}",
					ephemeral = True
				)
				await message.add_reaction("🎉")
				await sleep(0.5)

				await self.sqlite_manager.set_giveaway(
					channel_id =  current_channel.id,
					giveaway_id = giveaway_id, 
					time = time_end_at
				)

				giveaway_data = GiveawayData(
					message_id = giveaway_id,
					channel_id = current_channel.id,
					end_at = time_end_at
				)
				await self.__giveaway_timer.start(gws_data = giveaway_data)
 
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(GiveawaysSlash(bot = bot))