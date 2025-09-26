from typing import Optional
from datetime import datetime
from re import findall, fullmatch

_ONE_MINUTE = 60
_ONE_HOUR = 60 * _ONE_MINUTE
_ONE_DAY = 24 * _ONE_HOUR
_ONE_WEEK = 7 * _ONE_DAY
_ONE_YEAR = 365 * _ONE_DAY

class TimeUtils:
	@staticmethod
	def unix_time() -> int:
		return int(datetime.now().timestamp())

	@staticmethod
	def parse(time_str: str) -> Optional[int]:
		TIME_PATTERN = r"(?:\d+[ywdhms])+"
		time_str = time_str.strip().lower()

		if not time_str or not  fullmatch(TIME_PATTERN, time_str):
			return None

		pattern = r"(\d+)([ywdhms])"
		matches = findall(pattern = pattern, string = time_str)

		if not matches:
			return None

		total_seconds = 0 
		for value_str, unit in matches:
			try:
				value = int(value_str)

			except:
				return None
			
			match unit:
				case "y":
					total_seconds += value * _ONE_YEAR

				case "w":
					total_seconds += value * _ONE_WEEK

				case "d":
					total_seconds += value * _ONE_DAY

				case "h":
					total_seconds += value * _ONE_HOUR

				case "m":
					total_seconds += value * _ONE_MINUTE

				case "s":
					total_seconds += value 

				case _:
					return None
				
		return total_seconds if total_seconds > 0 else None