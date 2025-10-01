from dataclasses        import dataclass
from psycopg_pool       import AsyncConnectionPool
from psycopg 	        import AsyncConnection
from psycopg.rows       import TupleRow
from core_utils.logging import Log
from core_utils.guilds  import GuildUtils

_ACP = AsyncConnectionPool[AsyncConnection[TupleRow]]

@dataclass
class GwsManagerData:
	guild_id: 	int
	channel_id: int
	message_id: int
	end_at:		int

class GiveawayManager:
	def __init__(self, pool: _ACP) -> None:
		self.__pool = pool

	async def set_giveaway(self, gws_data: GwsManagerData) -> None:
		try:
			async with self.__pool.connection() as connect:
				await GuildUtils.add_guild_if_not_exists(
					connection = connect,
					guild_id   = gws_data.guild_id 
				)
				await connect.execute(
					"INSERT INTO giveaways (guild_id, channel_id, message_id, end_at) "
					"VALUES (%s, %s, %s, %s) "
					"ON CONFLICT (message_id, channel_id) "
					"DO UPDATE SET end_at = EXCLUDED.end_at",
				(
					gws_data.guild_id, gws_data.channel_id,
					gws_data.message_id, gws_data.end_at
				))
				await connect.commit()

		except Exception as error:
			Log.critical((
				f"Could not start giveaway in guild ID: {gws_data.guild_id}\n"
				f"With error: {error}"
			))
