#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
from redis import Redis
from healthcheck import HealthCheck, EnvironmentDump
from datetime import datetime
from config import Config

import json
import requests

config = Config()
health = HealthCheck()
envdump = EnvironmentDump()

auth = HTTPTokenAuth(header={ 'X-API-Key': config.API_KEY } )

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

@auth.verify_token
def verify_token(token=None):
    headers = request.headers
    key = headers.get('X-Api-Key')
    return key == config.API_KEY

@auth.error_handler
def auth_error(status):
    return jsonify({
        'message': 'Access Denied',
        'status': status
    }), 401

# ROUTES

@app.route('/', methods=['GET'], strict_slashes=False)
@auth.login_required
def index():
    return jsonify({
        'version': '0.0.1'
    })

@app.route('/rates', methods=['GET', 'POST'], strict_slashes=False)
@auth.login_required
def rates():
    tokens = []
    fiat_currencies = []
    exchange_rates = {}

    if request.is_json:
        content = request.get_json()

        tokens = content['coins'] if 'coins' in content else []
        fiat_currencies = content['currencies'] if 'currencies' in content else []
    else:
        args = request.args
        coins = args.get('coin') or args.get('coins')
        currencies = args.get('currency') or args.get('currencies')

        if coins:
            tokens = comma_separated_params_to_list(coins)

        if currencies:
            fiat_currencies = comma_separated_params_to_list(currencies)

    tokens = tokens if tokens else config.tokens()
    fiat_currencies = fiat_currencies if fiat_currencies else config.currencies()

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

@app.route('/health', methods=['GET'], strict_slashes=False)
@auth.login_required
def healthcheck():
    return health.run()


@app.route('/env', methods=['GET'], strict_slashes=False)
@auth.login_required
def env():
    return envdump.run()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
