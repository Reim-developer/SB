from typing import Optional
from discord import User, ButtonStyle, Embed
from discord.ui import View, Button
from discord.ext import commands
from datetime import datetime

class Widget(View):
	def __init__(self, url: str) -> None:
		self.url = url
		super().__init__(timeout = None)

		self.add_item(Button(
			style = ButtonStyle.url,
			label = "Download Avatar",
			url = f"{self.url}"
		))

class AvatarPrefix(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot 

	async def __author_avatar(
			self, ctx: commands.Context[commands.Bot]) -> None:
		this_guild = ctx.guild
		if not this_guild:
			return

		author = ctx.author

		if not author.avatar:
			await ctx.channel.send(
				content = ( 
					f"* Nu! {author.name}\n" \
					"* You do not have any avatar"
			))
			return

		avatar_url = author.avatar.url

		embed = Embed(
			title = f"{author.name} avatar",
			timestamp = datetime.now(),
			color = 0xf7c0b7
		)
		embed.set_image(url = avatar_url)
		embed.set_thumbnail(url = this_guild.icon.url if this_guild.icon else None)
		embed.set_footer(text = f"Requested by: {author.name}")

		await ctx.channel.send(embed = embed, view = Widget(url = avatar_url))

	async def __fetch_user_avatar(
			self, ctx: commands.Context[commands.Bot], 
			user: User) -> None:
		this_guild = ctx.guild

		if not this_guild:
			return
		
		avatar = user.avatar
		if not avatar:
			await ctx.channel.send(content = (
				f"* User {user} not found or they don't have an avatar"
			))

			return
		
		embed = Embed(
			title = f"{user.name} avatar",
			color = 0xfaf5cf,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(url = this_guild.icon.url if this_guild.icon else None)
		embed.set_image(url = avatar.url)
		embed.set_footer(text = f"Requested by {ctx.author}")

		await ctx.channel.send(embed = embed, view = Widget(url = avatar.url))

	@commands.command(aliases = ["av", "avt"])
	@commands.cooldown(1, 15, commands.BucketType.user)
	async def avatar(
			self, ctx: commands.Context[commands.Bot],
			user_target: Optional[User] = None) -> None:
		
		if not ctx.guild:
			return
		
		if not user_target:
			await self.__author_avatar(ctx = ctx)

		else:
			await self.__fetch_user_avatar(ctx = ctx, user = user_target)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(AvatarPrefix(bot = bot))