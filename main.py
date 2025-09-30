from sys 		  import argv
from sys 		  import stdout
from bot_manager import BotManager

def _show_help() -> None:
	stdout.write(
		f"Usage: {argv[0]} [OPTIONS]\n"
		"[+] For running bot in dev environment\n"
		f"[!] python {argv[0]} --dev\n"
		f"{'-' * 25}\n"
		"[+] For running bot in product environment\n"
		f"[!] python {argv[0]} --prod\n"
	)

def parse() -> None:
	MIN_ARGV    = 2 
	DEV_MODE    = "--dev"
	PROD_MODE   = "--prod"
	VALID_MODES = {DEV_MODE, PROD_MODE}

	if len(argv) < MIN_ARGV:
		_show_help()
		return
	
	mode = argv[1]
	if mode not in VALID_MODES:
		_show_help()
	
	BotManager((
		mode == DEV_MODE
	)).bot_run()

if __name__ == "__main__":
	parse()