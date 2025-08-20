from typing import Optional
from discord import Embed
from discord.ext import commands
from datetime import datetime

class MemberCountPrefix(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.__ctx: Optional[commands.Context[commands.Bot]] = None

	def __embed(self) -> Embed:
		if not self.__ctx:
			raise ValueError("'self.__cxt' requires not found")
		
		guild = self.__ctx.guild
		author = self.__ctx.author
		if not guild:
			return Embed()
		
		total_members = guild.member_count
		bot_members = sum(1 for member in guild.members if member.bot)
		real_member = total_members - bot_members if total_members else 'unknown'

		real_member_percent = (round(real_member / total_members * 100)) \
			if isinstance(real_member, int) and total_members else 'unknown'
		bot_members_percent = (round(bot_members / total_members * 100)) \
			if total_members else 'unknown'

		embed = Embed(
			title = f"{guild.name} | Member Count",
			description = (
				f"* Member(s): `{real_member}` members\n (`{real_member_percent}`%)\n" \
				f"* Bot(s): `{bot_members}` Bot(s) (`{bot_members_percent}`%)\n" \
				f"* Total: `{total_members if total_members else 'unknown'}` Members"
			),
			color = 0xfaebc3,
			timestamp = datetime.now()
		)
		embed.set_thumbnail(url = author.avatar.url if author.avatar else None)
		embed.set_footer(text = f"Requested by: {author.name}")

		return embed

	@commands.command(aliases = ["mc"])
	@commands.cooldown(1, 15, commands.BucketType.user)
	async def membercount(self, ctx: commands.Context[commands.Bot]) -> None:
		if not ctx.guild:
			return
		 
		self.__ctx = ctx
		embed = self.__embed()

		await ctx.channel.send(embed = embed)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(MemberCountPrefix(bot = bot))