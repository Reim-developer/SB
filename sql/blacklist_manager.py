from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from core_utils.logging import Log
from enum import Enum


_ACP = AsyncConnectionPool[AsyncConnection[TupleRow]]

class BlacklistResult(Enum):
	NOT_BLACKLISTED = 0
	BLACKLISTED 	= 1

class BlacklistManager:
	def __init__(self, pool: _ACP) -> None:
		self.__pool = pool

	async def set_blacklist_user(self, user_id: int ) -> None:
		try:
			async with self.__pool.connection() as connection: 
				await connection.execute(
					"INSERT INTO blacklist (user_id) "
					"VALUES (%s) "
					"ON CONFLICT (user_id) DO NOTHING",
				(user_id,))

				await connection.commit()
		
		except Exception as error:
			Log.critical(
				f"Could not set blacklist user ID: {user_id}\n"
				f"With error: {error}"
			)

	async def remove_blacklist_user(self, user_id: int) -> None:
		try:
			async with self.__pool.connection() as connection:
				await connection.execute(
					"DELETE FROM blacklist WHERE user_id = %s",
				(user_id,))

		except Exception as error:
			Log.critical(
				f"Could not remove blaclist user ID: {user_id}\n"
				f"With error: {error}"
			)

	async def is_blacklisted(self, user_id: int) -> BlacklistResult:
		B = BlacklistResult
		try:
			async with self.__pool.connection() as connection:
				cursor = await connection.execute(
					"SELECT 1 FROM blacklist WHERE user_id = %s",
				(user_id,))

				row = await cursor.fetchone()
				return B.BLACKLISTED if row else B.NOT_BLACKLISTED
			
		except Exception as error:
			Log.critical(
				f"Could not get user blacklisted ID: {user_id}\n"
				f"With error: {error}"
			)

			return B.NOT_BLACKLISTED
