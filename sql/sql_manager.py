from pathlib import Path
from typing import Any, Iterable, Optional
from aiosqlite import Row, connect

class SQLiteManager:
	def __init__(self, path: str) -> None:
		self.path = Path(path)
	
	def __is_database_exists(self) -> bool:
		return self.path.exists()
	
	async def init_if_not_exists(self) -> None:
		if not self.__is_database_exists():
			self.path.touch()

		async with connect(self.path.absolute()) as sqlite:
			await sqlite.execute(
		"""--sql
			CREATE TABLE IF NOT EXISTS sb_bot (
				guild_id INTEGER PRIMARY KEY,
				confession_channel_id INTEGER NOT NULL
			);
		""")
			await sqlite.execute(
		"""--sql
			CREATE TABLE IF NOT EXISTS blacklist (
				user_id INTEGER PRIMARY KEY
			);
		""")
			await sqlite.execute(
		"""--sql
			CREATE TABLE IF NOT EXISTS giveaways (
				message_id TEXT,
				channel_id TEXT,
				end_at INTEGER NOT NULL,
				PRIMARY KEY(message_id, channel_id)
			);
		""")
			await sqlite.commit()

	async def set_confession_channel(
			self, 
			guild_id: int, channel_id: int) -> None:
		
		async with connect(self.path.absolute()) as sqlite:
			await sqlite.execute(
		"""--sql
			INSERT OR REPLACE INTO sb_bot (guild_id, confession_channel_id)
			VALUES(?, ?)
		""", (guild_id, channel_id,))
			
			await sqlite.commit()

	async def set_blacklist_user(self, user_id: int) -> None:
		async with connect(self.path.absolute()) as sqlite:
			await sqlite.execute(
		"""--sql
			INSERT INTO blacklist (user_id)
			VALUES(?)
		""", (user_id,))
			
			await sqlite.commit()

	async def remove_blacklist_user(self, user_id: int) -> None:
		async with connect(self.path.absolute()) as sqlite:
			await sqlite.execute(
		"""--sql
			DELETE FROM blacklist WHERE user_id = ?
		""", (user_id,))
			await sqlite.commit()
			
	async def blacklist_user(self, user_id: int) -> bool:
		async with connect(self.path.absolute()) as sqlite:
			cursor = await sqlite.execute(
				"""--sql
					SELECT user_id FROM blacklist WHERE user_id = ?
				""", (user_id,))
			
			return await cursor.fetchone() is not None
		
	async def set_giveaway(self, channel_id: int, giveaway_id: int, time: int) -> None:
		async with connect(self.path.absolute()) as sqlite:
			await sqlite.execute(
				"""--sql
					INSERT OR REPLACE INTO giveaways (
						channel_id, message_id, end_at
					) 
					VALUES(?, ?, ?)
				""", (str(channel_id), str(giveaway_id), time,))
			
			await sqlite.commit()

	async def exec(self, query: str, parameters: Optional[Iterable[Any]]) -> None:
		async with connect(self.path.absolute()) as sqlite:
			await sqlite.execute(query, parameters)
			await sqlite.commit()

	async def confession_channel(self, guild_id: int) -> Optional[int]:
		async with connect(self.path.absolute()) as sqlite:
			cursor = await sqlite.execute(
			"""--sql
				SELECT confession_channel_id FROM sb_bot WHERE guild_id = ?
			""", (guild_id,))

			row = await cursor.fetchone()

			return row[0] if row else None
		
	async def fetch(self, query: str, params: Optional[Iterable[Any]]) -> Iterable[Row]:
		async with connect(self.path.absolute()) as sqlite:
			cursor = await sqlite.execute(query, params)

			return await cursor.fetchall()