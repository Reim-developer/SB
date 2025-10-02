from typing       		   import List, Optional
from psycopg_pool 		   import AsyncConnectionPool
from psycopg 			   import AsyncConnection
from psycopg.rows 	       import TupleRow
from caches.donation_cache import DonationCache
from core_utils.logging    import Log
from dataclasses 		   import dataclass
from decimal 			   import Decimal
from core_utils.guilds     import GuildUtils

_ACP = AsyncConnectionPool[AsyncConnection[TupleRow]]

@dataclass
class DonationData:
	guild_id:  int
	unit_name: str
	user_id:   int
	amount:    float

class DonationManager:
	def __init__(self, pool: _ACP, donation_cache: DonationCache) -> None:
		self.pool 		    = pool
		self.donation_cache = donation_cache

	async def set_log_channel(self, 
						guild_id: int, channel_id: int) -> None:
		try:
			async with self.pool.connection() as connect:
				await GuildUtils.add_guild_if_not_exists(
					connection = connect,
					guild_id   = guild_id 
				)
				await connect.execute(
					"""
						INSERT INTO donation_settings (guild_id, log_channel_id)
						VALUES (%s, %s)
						ON CONFLICT (guild_id)
						DO UPDATE SET log_channel_id = EXCLUDED.log_channel_id;
					""",(guild_id, channel_id)
				)

		except Exception as error:
			Log.critical((
				f"Could not set log channel in guild ID: {guild_id}\n"
				f"With error: {error}"
			))

	async def get_log_channel(self, guild_id: int) -> Optional[int]:
		try:
			async with self.pool.connection() as connect:
				await GuildUtils.add_guild_if_not_exists(
					connection = connect,
					guild_id   = guild_id 
				)
				row = await connect.execute(
					"""
						SELECT log_channel_id FROM donation_settings
						WHERE guild_id = %s;
					""", (guild_id,)
				)
				result = await row.fetchone()

				return result[0] if result and result[0] else None
			
		except Exception as error:
			Log.critical((
				f"Could not get log channel in guild ID: {guild_id}\n"
				f"With error: {error}"
			))
			return None

	async def add_unit_name(self,
						guild_id: int, unit_name: str) -> None:
		try:
			async with self.pool.connection() as connect:
				await GuildUtils.add_guild_if_not_exists(
					connection = connect,
					guild_id   = guild_id 
				)

				await connect.execute(
					"""
						INSERT INTO donation_units (guild_id, unit_name)
						VALUES (%s, %s)
						ON CONFLICT (guild_id, unit_name)
						DO NOTHING;
					""", (guild_id, unit_name)
				)
				
				await self.donation_cache.add_unit_name(
					guild_id  = guild_id,
					unit_name = unit_name
				)

		except Exception as error:
			Log.critical(
				f"Could not set money unit to guild ID: {guild_id}",
				f"With error: {error}"
			)

	async def get_unit_names(self, guild_id: int) -> List[str]:
		cached_units = await self.donation_cache.get_unit_names(
			guild_id = guild_id
		)
		if cached_units:
			return cached_units
	
		try:
			async with self.pool.connection() as connect:
				await GuildUtils.add_guild_if_not_exists(
					connection = connect,
					guild_id   = guild_id 
				)
				cursor = await connect.execute(
					"""
						SELECT unit_name FROM donation_units WHERE guild_id = %s
						ORDER BY unit_name
					""", (guild_id,)
				)
				rows = await cursor.fetchall()
				units = [row[0] for row in rows]

			await self.donation_cache.set_unit_names(
				guild_id = guild_id,
				units    = units
			)

			return units
			
		except Exception as error:
			Log.critical((
				f"Could not get money unit in guild ID: {guild_id}\n"
				f"With error: {error}"
			))
			return []

	async def add_donation(self, data: DonationData) -> None:
		amount_decimal = Decimal(str(data.amount))
		
		try:
			async with self.pool.connection() as connection:
				await GuildUtils.add_guild_if_not_exists(
					connection = connection,
					guild_id   = data.guild_id 
				)

				await connection.execute(
					"INSERT INTO donation_settings (guild_id) "
					"VALUES (%s) "
					"ON CONFLICT (guild_id) DO NOTHING;",
					(data.guild_id,)
				)

				await connection.execute(
					"""
						INSERT INTO donation_logs (guild_id, user_id, unit_name, amount)
						VALUES (%s, %s, %s, %s);
					""",(data.guild_id, data.user_id, data.unit_name, amount_decimal)
				)

		except Exception as error:
			Log.critical((
				f"Could not add donation to user ID: {data.user_id} in "
				f"guild ID: {data.guild_id}\n"
				f"With error: {error}"
			))

	async def get_user_donation(self, 
							 guild_id: int, user_id: int,
							 unit_name: str) -> Decimal:
		try:
			async with self.pool.connection() as connect:
				await GuildUtils.add_guild_if_not_exists(
					connection = connect,
					guild_id   = guild_id 
				)
				row = await connect.execute(
					"""
						SELECT COALESCE (SUM(amount), 0)
						FROM donation_logs
						WHERE guild_id = %s AND user_id = %s AND unit_name = %s;
					""", (guild_id, user_id, unit_name)
				)

				result = await row.fetchone()

				amount = result[0] if result else Decimal("0")
				return amount.normalize()
			
		except Exception as error:
			Log.critical((
				f"Could not get user ID: {user_id} donation in "
				f"guild ID: {guild_id}\n"
				f"With error: {error}"
			))

			return Decimal("0").normalize()

	