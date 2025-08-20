from discord import Embed, ButtonStyle
from discord.ext import commands
from datetime import datetime
from discord.ui import View, Button

class Widget(View):
	def __init__(
			self, invite_url: str, 
			support_server_url: str) -> None:
		super().__init__(timeout = None)

		self.add_item(Button(
			label = "My Invite URL",
			style = ButtonStyle.url,
			url = f"{invite_url}"
		))
		self.add_item(Button(
			label = "Support Server",
			style = ButtonStyle.url,
			url = f"{support_server_url}"
		))

class InvitePrefix(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.BOT_INVITE = "https://discord.com/oauth2/authorize?client_id=1045600567633915975&permissions=8&integration_type=0&scope=bot+applications.commands"
		self.SUPPORT_SERVER_INVITE = "https://discord.gg/S9Z4uUmXbA"

	@commands.command(aliases = ["inv", "invi"])
	@commands.cooldown(1, 15, commands.BucketType.user)
	async def invite(self, ctx: commands.Context[commands.Bot]) -> None:
		if not ctx.guild:
			return 
		
		author = ctx.author
		embed = Embed(
			title = f"Hello {author.name}",
			description = (
				f"* Be cute like a magical girl ~\n"
			),
			timestamp = datetime.now(),
			color = 0xf1d5f5
		)
		embed.set_thumbnail(url = author.avatar.url if author.avatar else None)
		embed.set_footer(text = f"Requested by {author.name}")

		await ctx.channel.send(
			embed = embed, 
			view = Widget(
				self.BOT_INVITE, self.SUPPORT_SERVER_INVITE
		))

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(InvitePrefix(bot = bot))
