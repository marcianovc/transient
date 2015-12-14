from os import environ
from os.path import join, dirname, isfile
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '..', '.env')
if isfile(dotenv_path):
    load_dotenv(dotenv_path)


ENV = environ.get("ENV", "production")
DEBUG = environ.get("DEBUG", False)

# API Settings
HOST = environ.get("HOST", "0.0.0.0")
PORT = environ.get("PORT", 3008)

# Database Settings
POSTGRES_HOST = environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = environ.get("POSTGRES_PORT", 5432)
POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE")
POSTGRES_USERNAME = environ.get("POSTGRES_USERNAME")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD")

# Coind Settings
DOGECOIN_RPC_HOST = environ.get("DOGECOIN_RPC_HOST", "localhost")
DOGECOIN_RPC_PORT = environ.get("DOGECOIN_RPC_PORT", 8332)
DOGECOIN_RPC_USERNAME = environ.get("DOGECOIN_RPC_USERNAME", "dogecoinrpc")
DOGECOIN_RPC_PASSWORD = environ.get("DOGECOIN_RPC_PASSWORD")

# Application Settings
PAYMENT_WEBHOOK_URL = environ.get("PAYMENT_WEBHOOK_URL")
