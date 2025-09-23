from dataclasses import dataclass
from typing import Dict, Optional
from discord import (
	TextChannel, Thread, Message, Embed
)
from discord.ui import View, Button
from discord.ext import commands
from sql.postgres_manager import PostgresManager
from asyncio import Task, create_task, sleep
from time import time
from random import choice
from datetime import datetime

class JumpToWidget(View):
	def __init__(self, url: str) -> None:
		super().__init__()
		self.url = url

		self.add_item(Button(
			label = "Jump to Giveaway",
			url = self.url
		))

@dataclass
class TimerData:
	bot: commands.Bot | commands.AutoShardedBot
	postgres_manager: PostgresManager

@dataclass
class GiveawayData:
	message_id: int
	channel_id: int 
	end_at: int

class GiveawayTimer:
	def __init__(self, timer_data: TimerData) -> None:
		self.__bot = timer_data.bot
		self.__postgre_manager = timer_data.postgres_manager
		self.__active: Dict[int, Task[None]] = {}
		self.__closed = False

	def __set_old_embed(self, message: Message) -> Embed:
		embed = Embed(
			title = "Giveaway has ended",
			description = message.embeds[0].description,
			color = message.embeds[0].color,
			timestamp = message.embeds[0].timestamp
		).set_footer(
			text = f"Giveaway ID: {message.id}"
		).set_thumbnail(
			url = message.embeds[0].thumbnail.url
		).set_image(url = message.embeds[0].image.url)

		return embed

	async def __wait_and_end(self, gws_data: GiveawayData) -> None:
		await sleep(gws_data.end_at - int(time()))

		self.__active.pop(gws_data.message_id, None)
		if self.__closed:
			return
		
		try:
			channel = await self.__bot.fetch_channel(gws_data.channel_id)
			if not channel:
				await self.__cleanup(message_id = gws_data.message_id)
				return
			
			if not isinstance(channel, (TextChannel, Thread)):
				return
			
			message: Optional[Message] = await channel.fetch_message(gws_data.message_id)
			if not message:
				await self.__cleanup(message_id = gws_data.message_id)
				return
			
			reaction = next(
				(react for react in message.reactions 
					if str(react.emoji) == "🎉"
				), None
			)

			await message.edit(
				embed = self.__set_old_embed(message = message)
			)

			gws_id = message.id
			gws_url = message.jump_url
			if not reaction or reaction.count == 1:

				await message.reply(
					content = f"Giveaway `{gws_id}` ends, no winner",
					view = JumpToWidget(url = gws_url)
				)
				return
			
			participants = [user async for user in reaction.users() if not user.bot]
			total_participants = len(participants)
			winner = choice(participants)
			win_rate = round(100 / total_participants)
			
			time_now = int(datetime.now().timestamp())

			await channel.send(
				content = (
					f"* Giveaway with id `{gws_id}` has ended\n" \
					f"* Winner: {winner.mention}\n" \
					f"* Win rate: `{win_rate}%`\n" \
					f"* End at: <t:{time_now}:R>"
				),
				view = JumpToWidget(url = gws_url)
			)
			await sleep(0.5)

		except Exception: ... # Ignore.

		finally:
			await self.__cleanup(message_id = gws_data.message_id)

	async def load_active_gws(self) -> None:
		assert self.__postgre_manager.pool is not None

		async with self.__postgre_manager.pool.connection() as connect:
			cursor = await connect.execute(
				"""--sql
					SELECT message_id, channel_id, end_at FROM giveaways
				""", ())
			
			rows = await cursor.fetchall()
		
		now = int(time())

		for msg_id_str, channel_id, end_at in rows:
			msg_id = int(msg_id_str)

			gws_data = GiveawayData(
				message_id = msg_id,
				channel_id = channel_id,
				end_at = end_at
			)
			if end_at <= now:
				await self.__wait_and_end(gws_data = gws_data)

			else:
				await self.start(gws_data = gws_data)

	async def __cleanup(self, message_id: int) -> None:
		assert self.__postgre_manager.pool is not None
		
		async with self.__postgre_manager.pool.connection() as connect:
			await connect.execute(
				"DELETE FROM giveaways WHERE message_id = %s",
				(message_id,)
			)

	async def start(self, gws_data: GiveawayData) -> None:
		if self.__closed:
			return
		
		if gws_data.message_id in self.__active:
			self.__active[gws_data.message_id].cancel()

		task = create_task(self.__wait_and_end(gws_data = gws_data))
		self.__active[gws_data.message_id] = task
