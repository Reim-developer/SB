# from typing import Optional
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from core_utils import Log

_ACP = AsyncConnectionPool[AsyncConnection[TupleRow]]

class ConfessionManager:
	def __init__(self, pool: _ACP) -> None:
		self.pool = pool

	async def set_confession_channel(self, 
							guild_id: int, channel_id: int) -> None:
		
		try:
			async with self.pool.connection() as connect:
				await connect.execute(
					"""
						INSERT INTO guild_configs (guild_id, confession_channel)
						VALUES (%s, %s)
						ON CONFLICT (guild_id)
						DO UPDATE SET confession_channel = EXCLUDED.confession_channel
					""", (guild_id, channel_id))
				
				await connect.commit()

		except Exception as error:
			Log.critical(
				f"Could not set confession channel "
				f"in guild: {guild_id} with error: {error}"
			)
			
