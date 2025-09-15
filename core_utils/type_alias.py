from discord import (
	TextChannel, Thread,
	AllowedMentions
)

CanSendMessageChannel = TextChannel | Thread
DisableAllMentions = AllowedMentions(
	everyone 	 = False,
	users 	 	 = False,
	roles 	 	 = False,
	replied_user = False
)