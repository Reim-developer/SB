from types import TracebackType
from typing import Optional, Self
from psycopg import AsyncConnection
from psycopg.rows import TupleRow
from psycopg.sql import SQL, Identifier
from psycopg_pool import AsyncConnectionPool
from core_utils.config import ConfigUtils
from core_utils.logging import StatusCode, Log
from urllib.parse import quote_plus

_ACP 		       = AsyncConnectionPool[AsyncConnection[TupleRow]]
_MAX_TIMEOUT       = 30
_BLACKLIST 		   = "blacklist"
_GIVEAWAYS		   = "giveaways"
_GUILD_CONFIGS     = "guild_configs" 
_DONATION_SETTINGS = "donation_settings"
_DONATION_LOGS     = "donation_logs"
_DONATION_TIERS    = "donation_tiers"

class PostgresManager:
	def __init__(self) -> None:
		self.config = ConfigUtils.database_config()
		self.pool: Optional[_ACP] = None
		self.TABLES = [
			_BLACKLIST, _GIVEAWAYS, _GUILD_CONFIGS, 
			_DONATION_LOGS, _DONATION_SETTINGS, _DONATION_TIERS
		]

	async def __aenter__(self) -> Self:
		await self.initialize()

		return self
	
	async def __aexit__(
			self, exc_type: Optional[type[BaseException]],
			exc_val: Optional[BaseException],
			exc_tb: Optional[TracebackType]) -> None:
		
		await self.close()

	async def initialize(self) -> None:
		if self.pool:
			return 

		try:
			self.pool = _ACP(
				conninfo = (
					f"postgresql://{self.config.user}:{quote_plus(self.config.password)}"
					f"@{self.config.host}:{self.config.port}/{self.config.dbname}"
				),
				timeout  = _MAX_TIMEOUT,
				open     = False
			)
			await self.pool.open()

			Log.info("Successfully initialize database") 

		except Exception as error:
			Log.critical(f"Could not initialize database with error: {error}")
			Log.fatal(StatusCode.DATABASE_CONNECT_ERR)

	async def __enable_security(self, connect: AsyncConnection) -> None:
		for table in self.TABLES:
			await connect.execute(
						SQL("ALTER TABLE {} ENABLE ROW LEVEL SECURITY;")
						.format(Identifier(table))
				)
			
			policy_name = "Full access for Discord Bot"
			result      = await connect.execute(SQL(
				"SELECT 1 FROM pg_policies WHERE tablename = %s AND policyname = %s"
			), (table, policy_name))
			exists 		= await result.fetchone()

			if not exists:
				await connect.execute(SQL(
						"CREATE POLICY {} " \
						"ON {} FOR ALL USING(true) WITH CHECK (true);"
					).format(Identifier(policy_name), Identifier(table)))
			
	async def init_if_not_exists(self) -> None:
		if not self.pool:
			await self.initialize()

		assert self.pool is not None
	
		try:
			async with self.pool.connection() as connect:
				await connect.execute(SQL(
					"""--sql
						CREATE TABLE IF NOT EXISTS {} (
							guild_id 		   	  BIGINT PRIMARY KEY,
							confession_channel_id BIGINT
						);
				   	""").format(Identifier(_GUILD_CONFIGS)))
				
				await connect.execute(SQL(
					"""--sql
						CREATE TABLE IF NOT EXISTS {} (
							user_id BIGINT PRIMARY KEY
						);
					""").format(Identifier(_BLACKLIST)))

				await connect.execute(SQL(
					""" 
						CREATE TABLE IF NOT EXISTS {} (
							message_id BIGINT,
							channel_id BIGINT,
							guild_id   BIGINT NOT NULL,
							end_at     BIGINT NOT NULL,
							PRIMARY    KEY (message_id, channel_id),
							FOREIGN    KEY (guild_id)
								REFERENCES {} (guild_id) 
								ON DELETE CASCADE
						);
					""").format(
						Identifier(_GIVEAWAYS), 
						Identifier(_GUILD_CONFIGS)
					))
				
				await connect.execute(SQL(
					"""
						CREATE TABLE IF NOT EXISTS {} (
							guild_id BIGINT PRIMARY KEY REFERENCES {} (guild_id) ON DELETE CASCADE,
							log_channel_id BIGINT,
							money_unit     TEXT NOT NULL DEFAULT 'credits'
					);"""
				).format(
					Identifier(_DONATION_SETTINGS),
					Identifier(_GUILD_CONFIGS)
				))

				await connect.execute(SQL(
					"""
						CREATE TABLE IF NOT EXISTS {} (
							id 		   BIGSERIAL PRIMARY KEY,
							guild_id   BIGINT NOT NULL REFERENCES {} (guild_id) ON DELETE CASCADE,
							user_id	   BIGINT NOT NULL,
							amount     NUMERIC(18, 4) NOT NULL CHECK (amount > 0),
							donated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
						);
					"""
				).format(
					Identifier(_DONATION_LOGS),
					Identifier(_DONATION_SETTINGS)
				))

				await connect.execute(SQL(
					"""
						CREATE TABLE IF NOT EXISTS {} (
							id         BIGSERIAL PRIMARY KEY,
							guild_id   BIGINT NOT NULL REFERENCES {} (guild_id) ON DELETE CASCADE,
							min_amount NUMERIC(18, 4) NOT NULL CHECK (min_amount > 0),
							role_id    BIGINT NOT NULL,
							UNIQUE (guild_id, min_amount),
							UNIQUE (guild_id, role_id)
						);
					"""
				).format(
					Identifier(_DONATION_TIERS),
					Identifier(_DONATION_SETTINGS)
				))

				await connect.execute(SQL(
					"""
						CREATE INDEX IF NOT EXISTS
						idx_donation_logs_guild_user ON
						{} (guild_id, user_id) INCLUDE (amount);
					""",
				).format(
					Identifier(_DONATION_LOGS)
				))
				
				await connect.commit()
				await self.__enable_security(connect = connect)

		except Exception as error:
			Log.critical(f"Could not execute SQL query with error: {error}")
			Log.fatal(StatusCode.EXECUTE_QUERY_ERR)

	async def close(self) -> None:
		if self.pool:
			await self.pool.close()
			self.pool = None
