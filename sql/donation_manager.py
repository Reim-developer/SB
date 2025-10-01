from typing       		import Optional
from psycopg_pool 		import AsyncConnectionPool
from psycopg 			import AsyncConnection
from psycopg.rows 	    import TupleRow
from core_utils.logging import Log
from dataclasses 		import dataclass
from decimal 			import Decimal
from core_utils.guilds  import GuildUtils

_ACP = AsyncConnectionPool[AsyncConnection[TupleRow]]

@dataclass
class DonationData:
	guild_id: int
	user_id:  int
	amount:   float

class DonationManager:
	def __init__(self, pool: _ACP) -> None:
		self.pool = pool

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

	async def set_money_unit(self,
						guild_id: int, money_unit: str) -> None:
		try:
			async with self.pool.connection() as connect:
				await GuildUtils.add_guild_if_not_exists(
					connection = connect,
					guild_id   = guild_id 
				)
				await connect.execute(
					"""
						INSERT INTO donation_settings (guild_id, money_unit)
						VALUES (%s, %s)
						ON CONFLICT (guild_id)
						DO UPDATE SET money_unit = EXCLUDED.money_unit;
					""", (guild_id, money_unit)
				)

		except Exception as error:
			Log.critical(
				f"Could not set money unit to guild ID: {guild_id}",
				f"With error: {error}"
			)

	async def get_money_unit(self, guild_id: int) -> str:
		_DEFAULT_UNIT = "credits"
		try:
			async with self.pool.connection() as connect:
				await GuildUtils.add_guild_if_not_exists(
					connection = connect,
					guild_id   = guild_id 
				)
				row = await connect.execute(
					"""
						SELECT money_unit FROM donation_settings WHERE guild_id = %s
					""", (guild_id,)
				)

				result = await row.fetchone()

				return result[0] if result else _DEFAULT_UNIT
			
		except Exception as error:
			Log.critical((
				f"Could not get money unit in guild ID: {guild_id}\n"
				f"With error: {error}"
			))
			return _DEFAULT_UNIT

	async def add_donation(self, data: DonationData) -> None:
		amount_decimal = Decimal(str(data.amount))
		
		try:
			async with self.pool.connection() as connection:
				await GuildUtils.add_guild_if_not_exists(
					connection = connection,
					guild_id   = data.guild_id 
				)
				await connection.execute(
					"""
						INSERT INTO donation_logs (guild_id, user_id, amount)
						VALUES (%s, %s, %s);
					""",(data.guild_id, data.user_id, amount_decimal)
				)

		except Exception as error:
			Log.critical((
				f"Could not add donation to user ID: {data.user_id} in "
				f"guild ID: {data.guild_id}\n"
				f"With error: {error}"
			))

	async def get_user_donation(self, guild_id: int, user_id: int) -> Decimal:
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
						WHERE guild_id = %s AND user_id = %s;
					""", (guild_id, user_id)
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

	