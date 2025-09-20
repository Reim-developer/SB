from tomllib import load
from psycopg2 import connect

with open(file = "toml/db_cfg.toml", mode = "rb") as toml_cfg:
	toml_data = load(toml_cfg)

connection = connect(
	dbname   = toml_data["database"]["dbname"],
	user     = toml_data["database"]["user"],
	host     = toml_data["database"]["host"],
	port     = toml_data["database"]["port"],
	password = toml_data["database"]["password"]
)