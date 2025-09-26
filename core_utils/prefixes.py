from discord.ext import commands
from discord import Message
from typing import Union, List

_DEFAULT_PREFIXES = "sb?"
def prefixes(bot: commands.Bot, message: Message) -> Union[List[str], str]:
	mention_prefixes = commands.when_mentioned(bot, message)
	default_prefixes = _DEFAULT_PREFIXES
	content 		 = message.content

	if content.lower().startswith(default_prefixes.lower()):
		actual_prefix = content[:len(default_prefixes)]

		return mention_prefixes + [actual_prefix]
	
	return mention_prefixes