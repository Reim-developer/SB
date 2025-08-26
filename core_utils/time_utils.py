from typing import Optional
from re import findall

_ONE_YEAR = 365
_ONE_WEEK = 7
_ONE_DAY = 24
_ONE_HOUR = 3600
_ONE_MINUTE = 60

class TimeUtils:
	@staticmethod
	def parse(time_str: str) -> Optional[int]:
		time_str = time_str.strip().lower()

		pattern = r"(\d+)([wdhms])"
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
					total_seconds += value * _ONE_YEAR * _ONE_DAY * _ONE_HOUR

				case "w":
					total_seconds += value * _ONE_WEEK * _ONE_DAY * _ONE_HOUR

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