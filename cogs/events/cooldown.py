from time import time
from asyncio import get_event_loop, sleep
from discord import Message
from typing import Optional
from discord.ext import commands 

class CooldownEvent(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot 
		self.__err_type: Optional[commands.CommandOnCooldown] = None
		self.__send = False
		self.__default_send_fallback: float = 15.5

	async def __cooldown_warnings(self, ctx: commands.Context[commands.Bot]) -> None:
		if not ctx.guild:
			return
		
		if not self.__send:
			cooldown = self.__err_type

			if cooldown:
				when = int(time() + cooldown.retry_after)

				message = await ctx.send((
					f"* Nu! {ctx.author}\n" \
					f"* Try again in <t:{when}:R>"
				))

			else:
				message = await ctx.send((
					f"* Nu! {ctx.author}\n" \
					f"* Try again in `unknown`"
				))

			self.__send = True

			bot_loop = get_event_loop()
			bot_loop.create_task(self.__reset_warnings(
				cooldown.retry_after if cooldown else self.__default_send_fallback,
				message
			))
	
	async def __reset_warnings(self, retry_after: float, msg: Message) -> None:
		await sleep(retry_after)
		self.__send = False

		if msg:
			try:
				await msg.delete()
			
			except Exception as error:
				print(f"[INFO] Could not delete message, error: {error}")

	@commands.Cog.listener()
	async def on_command_error(
			self, ctx: commands.Context[commands.Bot], 
			error: commands.CommandError) -> None:
		
		if isinstance(error, commands.CommandOnCooldown):
			self.__err_type = error
			await self.__cooldown_warnings(ctx = ctx)
	
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(CooldownEvent(bot = bot))