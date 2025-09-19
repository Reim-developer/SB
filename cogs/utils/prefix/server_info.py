from dataclasses import dataclass
from typing import Optional
from discord.ext import commands
from core_utils.type_alias import DisableAllMentions
from discord import Guild, Embed
from datetime import datetime
from widgets.server_info_widget import (
	GuildAssets, DownloadGuildAssetsWidget
)

_BUCKET_TYPE = commands.BucketType.user
_DAM 		 = DisableAllMentions
_MIN_ROLES	 = 1

@dataclass
class _DiscordGuildAssets:
	icon_url: 	Optional[str]
	banner_url: Optional[str]

@dataclass
class _DiscordGuild:
	name: 	   	 		str
	id: 	   	 		int
	owner_id:  	 		Optional[int]
	owner_name:  		Optional[str]
	boost_level: 		int
	vanity_url:  		Optional[str]
	created_at:  		datetime
	verification_level: int
	guild_assets: 		_DiscordGuildAssets
	role_count: 		int

def _impl_discord_guild(guild: Guild) -> _DiscordGuild:

	return _DiscordGuild(
		name 	 		   = guild.name,
		id 	 	 		   = guild.id,
		owner_id 		   = guild.owner_id,
		owner_name  	   = guild.owner.name if guild.owner else None,
		boost_level 	   = guild.premium_tier,
		vanity_url 		   = guild.vanity_url,
		created_at 		   = guild.created_at,
		verification_level = guild.verification_level.value,
		guild_assets 	   = _DiscordGuildAssets(
			icon_url   = guild.icon.url if guild.icon else None,
			banner_url = guild.banner.url if guild.banner else None
		),
		role_count 	   = len(guild.roles)
	)

class ServerInfoPrefix(commands.Cog):
	_D_G_W = DownloadGuildAssetsWidget
	_G 	   = GuildAssets

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	def __information_embed(self, data: _DiscordGuild) -> Embed:
		return (
			Embed(
				title 		= f"{data.name} Information",
				description = (
					f"* Guild Name: {data.name}\n" \
					f"* Created At: <t:{(
						int(data.created_at.timestamp())
					)}:R>\n" \
					f"* Owner: {(
						data.owner_name 
						if data.owner_name else  'Unknown Owner Name'
					)}\n" \
					f"* Owner ID: `{(
						data.owner_id
						if data.owner_id else 'Unknown Owner ID'
					)}`\n" \
					f"* Vanity URL: `{(
						data.vanity_url 
						if data.vanity_url else 'No Vanity URL'
					)}`\n" \
					f"* Verification Level: `{data.verification_level}`\n" \
					f"* Role Count: {(
						f'`{data.role_count}` Role(s)'
						if data.role_count > _MIN_ROLES
						else '`No any roles`'
					)}"
				),
				color 	    = 0xeeffc7
			)
			.set_thumbnail(
				url = (
					data.guild_assets.icon_url 
					if data.guild_assets.icon_url 
					else self.bot.user.avatar.url 
					if self.bot.user and self.bot.user.avatar else None
				)
			)
			.set_image(
				url = (
					data.guild_assets.banner_url 
					if data.guild_assets.banner_url else None
				)
			)
		)

	@commands.command(aliases = ["si", "sv", "server"])
	@commands.cooldown(rate = 1, per = 10, type = _BUCKET_TYPE)
	async def serverinfo(self, ctx: commands.Context[commands.Bot]) -> None:
		if not ctx.guild:
			await ctx.reply(
				content = (
					"Could not use this command in DM"
				),
				allowed_mentions = _DAM
			)
			return

		data = _impl_discord_guild(guild = ctx.guild)
		await ctx.channel.send(
			embed = self.__information_embed(data = data),
			view  = self._D_G_W(
				self._G(
					icon_url = (
						data.guild_assets.icon_url
						if data.guild_assets.icon_url else None
					),
					banner_url = (
						data.guild_assets.banner_url
						if data.guild_assets.banner_url else None
					)
				)
			)
		)
	
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(ServerInfoPrefix(bot = bot))