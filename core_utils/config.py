from dataclasses import dataclass
from tomllib import load
from pathlib import Path
from .logging import Log, StatusCode

@dataclass
class DatabaseConfig:
	dbname: str
	user: str
	port: int
	host: str 
	password: str

class ConfigUtils:
	def __init__(self) -> None: ...

	@staticmethod
	def gemini_api_keys() -> str:
		config_file = Path("config/config.toml")

		if not config_file.exists():
			Log.critical(f"TOML config file path not found: {config_file}")
			Log.fatal(StatusCode.READ_CONFIG_ERR)

		try:
			with open(file = "config/config.toml", mode = "rb") as toml_cfg:
				toml_data = load(toml_cfg)

		except Exception as error:
			Log.critical(f"Could not read or parse TOML string with error: {error}")
			Log.fatal(StatusCode.DATABASE_CONNECT_ERR)

		return toml_data["api"]["gemini_ai"]
			

	@staticmethod
	def database_config() -> DatabaseConfig:
		config_file = Path("config/config.toml")

		if not config_file.exists():
			Log.critical(f"TOML config file path not found: {config_file}")
			Log.fatal(StatusCode.READ_CONFIG_ERR)

		try:
			with open(file = "config/config.toml", mode = "rb") as toml_cfg:
				toml_data = load(toml_cfg)

		except Exception as error:
			Log.critical(f"Could not read or parse TOML string with error: {error}")
			Log.fatal(StatusCode.DATABASE_CONNECT_ERR)

		return DatabaseConfig(
			dbname   = toml_data["database"]["dbname"],
			user     = toml_data["database"]["user"],
			host     = toml_data["database"]["host"],
			port     = toml_data["database"]["port"],
			password = toml_data["database"]["password"]
		)
