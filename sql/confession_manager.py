from typing             import Optional
from psycopg_pool       import AsyncConnectionPool
from psycopg            import AsyncConnection
from psycopg.rows       import TupleRow
from core_utils.logging import Log
from core_utils.guilds  import GuildUtils

_ACP = AsyncConnectionPool[AsyncConnection[TupleRow]]

class ConfessionManager:
	def __init__(self, pool: _ACP) -> None:
		self.pool = pool

	async def set_confession_channel(self, 
							guild_id: int, channel_id: int) -> None:
		
		try:
			async with self.pool.connection() as connect:
				await GuildUtils.add_guild_if_not_exists(
					connection = connect,
					guild_id   = guild_id
				)

				await connect.execute(
					"""
						INSERT INTO guild_configs (guild_id, confession_channel_id)
						VALUES (%s, %s)
						ON CONFLICT (guild_id)
						DO UPDATE SET confession_channel_id = EXCLUDED.confession_channel_id
					""", (guild_id, channel_id))
				
				await connect.commit()

		except Exception as error:
			Log.critical(
				"Could not set confession channel "
				f"in guild: {guild_id}\n"
				f"with error: {error}"
			)
			

	async def get_confession_channel(self, guild_id: int) -> Optional[int]:
		try:
			async with self.pool.connection() as connect:
				row = await connect.execute((
					"SELECT confession_channel_id FROM guild_configs WHERE guild_id = %s"
				), (guild_id,))
				result = await row.fetchone()

				return result[0] if result else None
			
		except Exception as error:
			Log.critical(
				"Could not get confession channel "
				f"in guild: {guild_id}\n"
				f"With error: {error}"
			)
