#!/usr/bin/env python
# encoding: utf-8

import json
from flask import Flask, request, jsonify
from healthcheck import HealthCheck, EnvironmentDump
from datetime import datetime
from config import Config

app = Flask(__name__)
health = HealthCheck()
envdump = EnvironmentDump()

def redis_available():
    client = _redis_client()
    info = client.info()
    return True, 'redis ok'

health.add_check(redis_available)

def application_data():
    return {'maintainer': 'Justin R. Evans',
            'git_repo': 'https://github.com/jurevans/fiatconversion-api'}

envdump.add_section('application', application_data)

def is_key_valid(key):
    return key == Config.API_KEY

def comma_separated_params_to_list(param):
    result = []
    for val in param.split(','):
        if val:
            result.append(val.strip())
    return result

def getTimestamp():
    return datetime.timestamp(datetime.now())

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
            tokens = Config.DEFAULT_TOKENS

        if currencies:
            fiat_currencies = comma_separated_params_to_list(currencies)
        else:
            fiat_currencies = Config.DEFAULT_CURRENCIES

        for token in tokens:
            exchange_rates[token] = {}
            for fiat in fiat_currencies:
                exchange_rates[token][fiat] = 0.123

        return jsonify({
            'data': exchange_rates,
            'timestamp': getTimestamp(),
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

app.run(host='0.0.0.0', port=5000, debug=False)
