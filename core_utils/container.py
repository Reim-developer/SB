from typing import Optional
from sql.postgres_manager import PostgresManager

class _Container:
	def __init__(self) -> None:
		self.__postgres_manager: Optional[PostgresManager] = None

	def __set_prostgres_manager(self) -> None:
		if  not self.__postgres_manager:
			self.__postgres_manager = PostgresManager()
		
	def get_postgres_manager(self) -> PostgresManager:
		if not self.__postgres_manager:
			self.__set_prostgres_manager()

			assert self.__postgres_manager is not None
			return self.__postgres_manager
		
		return self.__postgres_manager
	
container_instance = _Container()