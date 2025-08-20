from json import load 
from discord import Intents, Object, HTTPException
from discord.ext import commands
from typing import Literal, Optional

with open(file = "./config/config.json", mode = "r", encoding = "utf-8") as config_file:
	json_data = load(config_file)
	BOT_TOKEN = json_data["BOT_TOKEN"]
	BOT_PREFIX = json_data["BOT_PREFIX"]

bot_intents = Intents.all()
bot_intents.presences = False

async def __setup_cogs() -> None:
	cog_list = [
		"cogs.events.cooldown",
		"cogs.events.cooldown_slash",
		"cogs.utils.prefix.invite",
		"cogs.utils.prefix.avatar",
		"cogs.utils.prefix.help",
		"cogs.utils.prefix.member_count",
		"cogs.utils.slash.set_confession",
		"cogs.utils.slash.confession"
	]

	for cog in cog_list:
		try:
			await bot.load_extension(cog)
			print(f"Load cog: {cog} successfully")

		except Exception as error:
			print(f"Could not load cog: {cog} with error: {error}")

bot = commands.Bot(
	command_prefix = BOT_PREFIX, 
	help_command = None, 
	intents = bot_intents,
	case_insensitive = True
)

@bot.command()
@commands.is_owner()
async def sync(
    ctx: commands.Context[commands.Bot], 
    guilds: commands.Greedy[Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
	if not guilds:
		if spec == "~":
			synced = await ctx.bot.tree.sync(guild = ctx.guild)
		elif spec == "*":
			if ctx.guild:
				ctx.bot.tree.copy_global_to(guild = ctx.guild)
				synced = await ctx.bot.tree.sync(guild = ctx.guild)
		elif spec == "^":
			ctx.bot.tree.clear_commands(guild = None)

			await ctx.bot.tree.sync(guild = ctx.guild)
			synced = []
		else:
			synced = await ctx.bot.tree.sync()

			await ctx.send(
				f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
			)
			return

	ret = 0
	for guild in guilds:
		try:
			await ctx.bot.tree.sync(guild=guild)
		except HTTPException:
			print("")
		else:
			ret += 1

	await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

@bot.event
async def on_ready() -> None:
	await __setup_cogs()
	await bot.tree.sync()
	print(f"Online as: {bot.user.name if bot.user else  'unknown bot name'}")

bot.run(token = BOT_TOKEN)