from psycopg 	 			   import AsyncConnection
from psycopg.sql 			   import SQL, Identifier
from core_utils.logging import Log
from sql.tables  			   import Tables

class GuildUtils:
	def __init__(self) -> None: ...

	@staticmethod
	async def add_guild_if_not_exists(
				connection: AsyncConnection, guild_id: int) -> None:
		try:
			await connection.execute(SQL(
				"INSERT INTO {} (guild_id) VALUES (%s) "
				"ON CONFLICT (guild_id) DO NOTHING").format(Identifier(Tables.GUILDS)),
				(guild_id,)
			)

		except Exception as error:
			Log.critical(
				f"Could not add guild (ID: {guild_id})\n"
				f"With error: {error}"
			)