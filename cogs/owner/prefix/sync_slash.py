from discord.ext import commands
from discord import Object
from typing import Optional, Literal

class SyncSlashPrefix(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	@commands.command()
	@commands.is_owner()
	async def sync(
			self, ctx: commands.Context[commands.Bot],
			guilds: commands.Greedy[Object], 
			spec: Optional[Literal["~", "*", "^"]] = None) -> None:
		if not ctx.guild:
			return
		
		if not guilds:
			match spec:
				case "~":
					synced = await ctx.bot.tree.sync(guild = ctx.guild)
				
				case "^":
					ctx.bot.tree.clear_commands(guild = None)
					await ctx.bot.tree.sync(guild = ctx.guild)
					synced = []

				case "*":
					ctx.bot.tree.copy_global_to(guild = ctx.guild)
					synced = await ctx.bot.tree.sync(guild = ctx.guild)

				case _:
					synced = await ctx.bot.tree.sync()

			await ctx.channel.send(f"Synced {len(synced)} command {(
				'globally' if spec is None else 'to the current guild'
			)}")

		ret = 0
		for guild in guilds:
			try:
				await ctx.bot.tree.sync(guild = guild)
			
			except Exception as error:
				print(f"Could not sync slash command with error: {error}")
				return
			
			else:
				ret += 1
		
		await ctx.channel.send(f"Synced the tree to {ret}/{len(guilds)}")

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(SyncSlashPrefix(bot = bot))