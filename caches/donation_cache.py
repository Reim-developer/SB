from typing 			import List
from redis.asyncio   	import Redis
from asyncio            import Lock
from core_utils.logging import Log
from json 				import loads, dumps

class DonationCache:
	_DEFAULT_TTL = 2400 # 40 minutes

	def __init__(self, redis: Redis) -> None:
		self.redis  = redis
		self.__lock = Lock()

	def __get_key(self, guild_id: int) -> str:
		return f"donation_units:{guild_id}"
	
	async def get_unit_names(self, guild_id: int) -> List[str]:
		key = self.__get_key(guild_id = guild_id)

		try:
			data = await self.redis.get(key)

			return loads(data) if data else []

		except Exception as error:
			Log.critical(
				f"Could not get unit name(s) of guild ID: {guild_id}\n"
				f"With error: {error}"
			)

			return []
	
	async def add_unit_name(self, guild_id: int, unit_name: str) -> None:
		key = self.__get_key(guild_id = guild_id)

		try:
			async with self.__lock:
				current_units = await self.get_unit_names(guild_id = guild_id)

				if unit_name not in current_units:
					current_units.append(unit_name)
					current_units.sort()

					await self.redis.setex(
						key,
						self._DEFAULT_TTL,
						dumps(current_units)
					)

		except Exception as error:
			Log.critical(
				f"Could not add unit name for guild ID: {guild_id}\n"
				f"With error: {error}"
			)

	async def set_unit_names(self, guild_id: int, units: List[str]) -> None:
		key = self.__get_key(guild_id = guild_id)

		try:
			units.sort()

			await self.redis.setex(
				key, self._DEFAULT_TTL,
				dumps(units)
			)

		except Exception as error:
			Log.critical(
				f"Could not set unit name(s) for guild ID: {guild_id}\n"
				f"With error: {error}"
			)

	async def delete_unit_names(self, guild_id: int) -> None:
		key = self.__get_key(guild_id = guild_id)

		try:
			await self.redis.delete(key)

		except Exception as error:
			Log.critical(
				f"Could not delete unit name(s) for guild ID: {guild_id}\n"
				f"With error: {error}"
			)
