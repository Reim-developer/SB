from pathlib import Path
from typing import Optional
from aiosqlite import connect

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
			
			await sqlite.commit()

	async def set_confession_channel(
			self, 
			guild_id: int, channel_id: int) -> None:
		
		async with connect(self.path.absolute()) as sqlite:
			await sqlite.execute(
		"""--sql
			INSERT OR REPLACE INTO sb_bot (guild_id, confession_channel_id)
			VALUES(?, ?)
		""", (guild_id, channel_id))
			
			await sqlite.commit()

	async def confession_channel(self, guild_id: int) -> Optional[int]:
		async with connect(self.path.absolute()) as sqlite:
			cursor = await sqlite.execute(
			"""--sql
				SELECT confession_channel_id FROM sb_bot WHERE guild_id = ?
			""", (guild_id,))

			row = await cursor.fetchone()

			return row[0] if row else None