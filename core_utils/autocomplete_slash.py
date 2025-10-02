from discord              import Interaction, app_commands
from typing  		      import List 
from sql.donation_manager import DonationManager

class AutoComplete:
	def __init__(self, donation_manager: DonationManager) -> None:
		self.__donation_manager = donation_manager
	
	async def unit_autocomplete(self, 
							   interaction: Interaction, 
							   current: str) -> List[app_commands.Choice[str]]:
		if not interaction.guild:
			return []
		
		units 	 = await self.__donation_manager.get_unit_names(interaction.guild.id)
		filtered = [
			unit for unit in units
			if current.lower() in unit.lower() 
		]

		return [
			app_commands.Choice(name = unit, value = unit)
			for unit in filtered[:25]
		]