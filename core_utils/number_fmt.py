
from decimal import Decimal


class Number:
	@staticmethod
	def fmt_donation(amount: Decimal) -> str:
		return f"{amount.normalize():f}"