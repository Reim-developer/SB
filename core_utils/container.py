from typing 			  import Optional
from sql.postgres_manager import PostgresManager
from caches.redis_manager import RedisManager
from .config			  import ConfigUtils

class _Container:
	def __init__(self) -> None:
		self.__postgres_manager: Optional[PostgresManager] = None
		self.__redis_manager: Optional[RedisManager]       = None

	def __set_postgres_manager(self) -> None:
		if not self.__postgres_manager:
			self.__postgres_manager = PostgresManager()
		
	def get_postgres_manager(self) -> PostgresManager:
		if not self.__postgres_manager:
			self.__set_postgres_manager()

			assert self.__postgres_manager is not None
			return self.__postgres_manager
		
		return self.__postgres_manager
	
	def __set_redis_manager(self) -> None:
		if not self.__redis_manager:
			self.__redis_manager = RedisManager(ConfigUtils.redis())

	def get_redis_manager(self) -> RedisManager:
		if not self.__redis_manager:
			self.__set_redis_manager()

			assert self.__redis_manager is not None
			return self.__redis_manager
		
		return self.__redis_manager
	
container_instance = _Container()