from logging import basicConfig, getLogger
from typing import TypeVarTuple, Unpack, NoReturn
from enum import Enum
from sys import exit

_TS = TypeVarTuple("_TS")
_UP = Unpack

basicConfig(
	level   = "INFO",
	format  = "%(asctime)s - %(levelname)s - %(message)s",
	datefmt = "%Y-%m-%d %H:%M:%S" 
)
logger = getLogger(__name__)

def _to_string(*args: _UP[_TS]) -> str:
	return " ".join(str(arg) for arg in args)

class StatusCode(Enum):
	READ_CONFIG_ERR      = 1
	DATABASE_CONNECT_ERR = 2
	EXECUTE_QUERY_ERR    = 3

class Log:
	@staticmethod
	def debug(*args: _UP[_TS]) -> None:
		logger.debug(_to_string(*args))

	@staticmethod
	def critical(*args: _UP[_TS]) -> None:
		logger.critical(_to_string(*args))

	@staticmethod
	def info(*args: _UP[_TS]) -> None:
		logger.info(_to_string(*args))

	@staticmethod
	def fatal(code: StatusCode) -> NoReturn:
		exit(code.value)