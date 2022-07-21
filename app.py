#!/usr/bin/env python
# encoding: utf-8

import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from redis import Redis
from healthcheck import HealthCheck, EnvironmentDump
from datetime import datetime
from config import Config

config = Config()
health = HealthCheck()
envdump = EnvironmentDump()

app = Flask(__name__)
CORS(app, resources={r"/rates/*": {"origins": "*"}})
redis_client = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,
                     password=config.REDIS_PASSWORD, db=config.REDIS_DB, decode_responses=True)

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
    url = f"{config.exchange_api()}/{token}/{fiat}/"
    headers = {'X-CoinAPI-Key' : config.THIRD_PARTY_KEY}
    response = requests.get(url, headers=headers)
    response_json = response.json()
    data = {}

    if response:
        data = {
            'coin': response_json['asset_id_base'] or token,
            'currency': response_json['asset_id_quote'] or fiat,
            'rate': response_json['rate'],
            'timestamp': response_json['time'],
        }

    return data

# ROUTES

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'version': '0.0.1'
    })

@app.route('/rates/', methods=['GET', 'POST'])
def rates():
    headers = request.headers
    auth = headers.get('X-Api-Key')

    if not is_key_valid(auth):
        return jsonify({'message': 'ERROR: Unauthorized'}), 401
    else:
        exchange_rates = {}
        args = request.args
        coins = args.get('coin') or args.get('coins')
        currencies = args.get('currency') or args.get('currencies')

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
                expires_key = f"{key}/expires"
                unexpired = redis_client.get(expires_key)
                data = redis_client.hgetall(key)

                if not unexpired:
                    data = fetch_exchange_rate(token, fiat)
                    if bool(data):
                        redis_client.set(expires_key, config.TTL, ex=config.TTL)
                        redis_client.hset(name=make_storage_key(token, fiat), mapping=data)
                    else:
                        data = {}

                # Provide conversion rate in float
                if bool(data):
                    rate = data['rate']
                    data['rate'] = float(rate) if rate else 0

                exchange_rates[token][fiat] = data

        return jsonify({
            'data': exchange_rates,
            'timestamp': get_timestamp(),
        })

@app.route('/health/', methods=['GET'])
def healthcheck():
    headers = request.headers
    auth = headers.get('X-Api-Key')

    if is_key_valid(auth):
        return health.run()
    else:
        return jsonify({'message': 'ERROR: Unauthorized'}), 401

@app.route('/env/', methods=['GET'])
def env():
    headers = request.headers
    auth = headers.get('X-Api-Key')

    if is_key_valid(auth):
        return envdump.run()
    else:
        return jsonify({'message': 'ERROR: Unauthorized'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
