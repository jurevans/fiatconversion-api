import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TTL_ONE_HOUR = 3600

class Config(object):
  def __init__(self):
    self.API_KEY = os.environ.get('API_KEY')
    self.DEFAULT_TOKENS = ['BTC', 'ATOM', 'ETH', 'DOT']
    self.DEFAULT_CURRENCIES = ['USD', 'EUR']
    self.REDIS_HOST=os.environ.get('REDIS_HOST') or '127.0.0.1'
    self.REDIS_PORT=os.environ.get('REDIS_PORT') or 6379
    self.REDIS_PASSWORD=os.environ.get('REDIS_PASSWORD')
    self.REDIS_DB=os.environ.get('REDIS_DB') or 0
    self.THIRD_PARTY_KEY = os.environ.get('THIRD_PARTY_KEY')
    self.THIRD_PARTY_URL = 'https://rest.coinapi.io/v1/exchangerate'
    self.TTL = os.environ.get('TTL') or TTL_ONE_HOUR

  def tokens(self):
    return self.DEFAULT_TOKENS

  def currencies(self):
    return self.DEFAULT_CURRENCIES
