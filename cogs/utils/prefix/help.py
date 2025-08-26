from json_helper import emoji, prefix
from typing import Optional
from discord.ext import commands
from discord import Embed 
from datetime import datetime

class HelpPrefix(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.__ctx: Optional[commands.Context[commands.Bot]] = None

	def __embed(self) -> Embed:
		utils_emo = emoji("UTILS")
		aliases_emo= emoji("ALIASES")
		dot_bottom_emo = emoji("DOT_BOTTOM")
		prefix_emo = emoji("PREFIX")
		separator_emo = emoji("SEPARATOR")
		slash_emo = emoji("SLASH")
		anime_emo = emoji("ANIME")
		bot_prefix = prefix()

		bot_user = self.bot.user

		embed = Embed(
			title = f"`{bot_user.name if bot_user else 'unknown'}` Help Page",
			description = (
				f"{utils_emo} **Utils Commands:**\n" \
				f"*	{prefix_emo} `{bot_prefix}` avatar\n" \
				f"* {aliases_emo} Aliases: [`av`, `avt`]\n" \
				f"{dot_bottom_emo} Show your avatar or another user avatar.\n" \
				f"{separator_emo}\n" \
				f"*	{prefix_emo} `{bot_prefix}` invite\n" \
				f"* {aliases_emo} Aliases: [`inv`, `invit`]\n" \
				f"{dot_bottom_emo} Show bot invite URL & support server.\n" \
				f"{separator_emo}\n" \
				f"* {slash_emo} `/set_confession`\n" \
				f"* {aliases_emo} Aliases: `None`\n" \
				f"{dot_bottom_emo} Setup your confession channel\n" \
				f"{separator_emo}\n" \
				f"* {slash_emo} `/confession`\n" \
				f"* {aliases_emo} Aliases: `None`\n" \
				f"{dot_bottom_emo} Send your message to confession channel\n" \
				f"{separator_emo}\n" \
				f"{anime_emo} **Anime Commands:**\n" \
				f"* {slash_emo} `my_animelist_info`\n" \
				f"* {aliases_emo} Aliases: `None`\n" \
				f"{dot_bottom_emo} Show anime information with `MyAnimeList` ID\n" \
				f"{separator_emo}\n" \
				f"🎉 **Giveaway Commands:**\n" \
				f"* {slash_emo} `giveaway_create`\n" \
				f"* {aliases_emo} Aliases: `None`\n" \
				f'{dot_bottom_emo} Create a giveaway\n' 
			),
			timestamp = datetime.now(),
			color = 0xfac7c3
		)
		if self.__ctx:
			author = self.__ctx.author
			embed.set_thumbnail(url = author.avatar.url if author.avatar else None)
			embed.set_footer(text = f"Requested by {author.name}")

		return embed

	@commands.command()
	@commands.cooldown(1, 15, commands.BucketType.user)
	async def help(
		self, 
		ctx: commands.Context[commands.Bot]) -> None:

		if not ctx.guild:
			return
		
		self.__ctx = ctx
		embed = self.__embed()

		await ctx.channel.send(embed = embed)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(HelpPrefix(bot = bot))