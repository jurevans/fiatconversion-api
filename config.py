import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

'''DEFAULTS'''
TTL_TWO_HOURS = 7200
DEFAULT_TOKENS = ['BTC', 'ATOM', 'ETH', 'DOT']
DEFAULT_CURRENCIES = ['USD', 'EUR']
EXCHANGE_RATE_API = "https://rest.coinapi.io/v1/exchangerate"

class Config(object):
  def __init__(self):
    self.API_KEY = os.environ.get('API_KEY')
    self.DEFAULT_TOKENS = DEFAULT_TOKENS
    self.DEFAULT_CURRENCIES = DEFAULT_CURRENCIES
    self.REDIS_HOST=os.environ.get('REDIS_HOST') or '127.0.0.1'
    self.REDIS_PORT=os.environ.get('REDIS_PORT') or 6379
    self.REDIS_PASSWORD=os.environ.get('REDIS_PASSWORD')
    self.REDIS_DB=os.environ.get('REDIS_DB') or 0
    self.THIRD_PARTY_KEY = os.environ.get('THIRD_PARTY_KEY')
    self.EXCHANGE_RATE_API = os.environ.get('EXCHANGE_RATE_API') or EXCHANGE_RATE_API
    self.TTL = int(os.environ.get('TTL')) or TTL_TWO_HOURS

  def tokens(self):
    return self.DEFAULT_TOKENS

  def currencies(self):
    return self.DEFAULT_CURRENCIES

  def exchange_api(self):
    return self.EXCHANGE_RATE_API
