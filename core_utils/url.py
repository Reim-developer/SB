from urllib.parse import urlparse

class URLUtils:
	def __init__(self) -> None: ...

	@staticmethod
	def valid_url(url: str) -> bool:
		try:
			result = urlparse(url = url)

			return all([result.scheme, result.netloc])
		
		except:
			return False