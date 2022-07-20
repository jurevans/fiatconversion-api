#!/usr/bin/env python
# encoding: utf-8

import json
import requests
from flask import Flask, request, jsonify
from redis import Redis
from healthcheck import HealthCheck, EnvironmentDump
from datetime import datetime
from config import Config

config = Config()
health = HealthCheck()
envdump = EnvironmentDump()

app = Flask(__name__)
redis_client = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,
                     password=config.REDIS_PASSWORD, db=config.REDIS_DB)

redis_client.set_response_callback('GET', lambda i: float(i) if i else 0)

def redis_available():
    info = redis_client.info()
    return True, 'redis ok'

health.add_check(redis_available)

def application_data():
    return {'maintainer': 'Justin R. Evans',
            'git_repo': 'https://github.com/jurevans/fiatconversion-api'}

envdump.add_section('application', application_data)

def is_key_valid(key):
    return key == config.API_KEY

def comma_separated_params_to_list(param):
    result = []
    for val in param.split(','):
        if val:
            result.append(val.strip())
    return result

def get_timestamp():
    return datetime.timestamp(datetime.now())

def make_storage_key(token, fiat):
    return f"{token}/{fiat}"

def fetch_exchange_rate(token, fiat):
    url = f"{config.THIRD_PARTY_URL}/{token}/{fiat}/"
    headers = {'X-CoinAPI-Key' : config.THIRD_PARTY_KEY}
    response = requests.get(url, headers=headers)
    response_json = response.json()
    return response_json['rate'] or 0

# ROUTES

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'version': '0.0.1'
    })

@app.route('/rates', methods=['GET', 'POST'])
def rates():
    headers = request.headers
    auth = headers.get('X-Api-Key')

    if not is_key_valid(auth):
        return jsonify({'message': 'ERROR: Unauthorized'}), 401
    else:
        exchange_rates = {}
        args = request.args
        coins = args.get('coins')
        currencies = args.get('currencies')

        if coins:
            tokens = comma_separated_params_to_list(coins)
        else:
            tokens = config.tokens()

        if currencies:
            fiat_currencies = comma_separated_params_to_list(currencies)
        else:
            fiat_currencies = config.currencies()

        for token in tokens:
            exchange_rates[token] = {}
            for fiat in fiat_currencies:
                key = make_storage_key(token, fiat)
                rate = redis_client.get(key)

                if not rate:
                    rate = fetch_exchange_rate(token, fiat)
                    redis_client.set(make_storage_key(token, fiat), rate, ex=config.TTL)

                exchange_rates[token][fiat] = rate

        return jsonify({
            'data': exchange_rates,
            'timestamp': get_timestamp(),
        }) 

@app.route('/health', methods=['GET'])
def healthcheck():
    headers = request.headers
    auth = headers.get('X-Api-Key')

    if is_key_valid(auth):
        return health.run()
    else:
        return jsonify({'message': 'ERROR: Unauthorized'}), 401

@app.route('/env', methods=['GET'])
def env():
    headers = request.headers
    auth = headers.get('X-Api-Key')

    if is_key_valid(auth):
        return envdump.run()
    else:
        return jsonify({'message': 'ERROR: Unauthorized'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
