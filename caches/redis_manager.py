from typing            import Optional
from core_utils.config import CacheConfig
from redis.asyncio     import Redis


class RedisManager:
	def __init__(self, config: CacheConfig) -> None:
		self.__config 				  = config
		self.__redis: Optional[Redis] = None

	def new_or_get(self) -> Redis:
		if not self.__redis:
			self.__redis =  Redis (
				host 	 = self.__config.host,
				port 	 = self.__config.port,
				password = self.__config.password
			)
			return self.__redis
		
		return self.__redis
	