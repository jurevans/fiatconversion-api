import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config(object):
  def __init__(self):
    self.API_KEY = os.environ.get('API_KEY')
    self.DEFAULT_TOKENS = ['BTC', 'ATOM', 'ETH', 'DOT']
    self.DEFAULT_CURRENCIES = ['USD', 'EUR']
    self.REDIS_HOST=os.environ.get('REDIS_HOST') or '127.0.0.1'
    self.REDIS_PORT=os.environ.get('REDIS_PORT') or 6379
    self.THIRD_PARTY_KEY = os.environ.get('THIRD_PARTY_KEY')
    self.THIRD_PARTY_URL = 'https://api.coinlayer.com/'

  def tokens(self):
    return self.DEFAULT_TOKENS

  def currencies(self):
    return self.DEFAULT_CURRENCIES
