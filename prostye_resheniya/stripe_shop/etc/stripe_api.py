import os


def get_stripe_client_api_key(currency: str) -> str:
    env_key = f'{currency.upper()}_STRIPE_CLIENT_API_KEY'
    return os.environ[env_key]


def get_stripe_server_api_key(currency: str) -> str:
    env_key = f'{currency.upper()}_STRIPE_SERVER_API_KEY'
    return os.environ[env_key]
