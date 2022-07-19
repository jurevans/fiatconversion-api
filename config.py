import os

class Config(object):
  API_KEY = os.environ.get('API_KEY')
  DEFAULT_TOKENS = ['BTC', 'ATOM', 'ETH', 'DOT']
  DEFAULT_CURRENCIES = ['USD', 'EUR']
  REDIS_HOST=os.environ.get('REDIS_HOST') or '127.0.0.1'
  REDIS_PORT=os.environ.get('REDIS_PORT') or 6379
  THIRD_PARTY_KEY = os.environ.get('THIRD_PARTY_KEY')
  THIRD_PARTY_URL = 'https://api.coinlayer.com/' # Example
