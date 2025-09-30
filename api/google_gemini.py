from google import genai
from core_utils.logging import Log

class GoogleGeminiAPI:
	_AGENT_PROMPT = (
		 "You are an expert academic tutor named Professor Hotaru Futaba. Your role is to assist students with learning, "
		"homework, concept explanations, problem-solving, study strategies, and critical thinking. "
		"Always be clear, patient, encouraging, and pedagogically sound. "
		"Crucially, detect the language used in the user's query and respond in the same language. "
		"If the query is in Vietnamese, reply in Vietnamese; if in English, reply in English; and so on. "
		"Never assume the user’s proficiency level—ask clarifying questions when needed, and adapt your explanations accordingly. "
		"Focus on understanding, not just answers. Guide the student to think, not just copy."
	)
	_MODEL = "gemini-2.0-flash"

	def __init__(self, api_keys: str) -> None:
		self.__api_keys = api_keys
		self.__client   = genai.Client(
			api_key = self.__api_keys
		)

	def response(self, question: str) -> str:
		full_prompt = f"{self._AGENT_PROMPT}\n\nUser Query: {question}"

		try:
			# It's type-valid.
			# The reason for 'type: ignore'
			# is because it seems that the library doesn't have
			# enough stubs for the function signature
			response = self.__client.models.generate_content( # type: ignore
				model 	 = self._MODEL, 
				contents = full_prompt 
			)

			return (
				response.text.strip() 
				if response.text
				else "Could not generate answer for you. Please try again"
			)
		
		except Exception as error:
			Log.critical(f"Could not generate prompt with error: {error}")
			return "Could not generate answer for you. Please try again"