# fiatconversion-api

This is a simple Rest API for caching fiat-conversion rates from a third-party API, and may potentially serve other useful data in the future.

## Table of Contents

- [Installation](#installation)
- [Running the development server](#running-the-development-server)
- [Environment Configuration](#environment-configuration)
- [Endpoints](#endpoints)

## Installation

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
. venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

[ [Table of Contents](#table-of-contents) ]

## Running the development server

```bash
# Run app.py as an executable
./app.py

# Alternatively, call with python
python3 app.py

# Your server will be available at http://127.0.0.1:5000/
# Make sure to send requests with the x-api-key header value which
# matches the key in your .env file
```

[ [Table of Contents](#table-of-contents) ]

## Environment Configuration

Create a `.env` file with the following keys defined:

```bash
# Key used by x-api-key header to authorize protected routes:
API_KEY=THIS_IS_MY_API_KEY

# Redis authentication
REDIS_AUTH=MY_REDIS_SECRET

# Redis host (if not localhost)
REDIS_HOST=domain.of.redis

# Redis port (if not default)
REDIS_PORT=6379
```

[ [Table of Contents](#table-of-contents) ]

## Endpoints

The development

- `/` - Index
- `/rates` - Get default conversion rates (`GET`|`POST`)
- `/rates?coins=BTC,ETH,DOT` - Specify coins for which to query. Default currencies will be used.
- `/rates?currencies=USD,EUR` - Specify currencies. Default coins will be used.
- `/rates?coins=BTC,ETH,DOT,ATOM&currencies=USD,YEN,EUR` - Specify both coins and currencies, no defaults.
- `/health` - Health check
- `/env` - Environment variables

**POST** Example with cURL

```bash
curl --request POST http://127.0.0.1:5000/rates --header "X-Api-Key:MY_SECRET_API_KEY" --data "coins=BTC,EUR&currencies=USD,EUR,YEN"
```

**SAMPLE OUTPUT**

```json
{
  "rates": {
    "ATOM": {
      "EUR": 0.123,
      "USD": 0.123
    },
    "BTC": {
      "EUR": 0.123,
      "USD": 0.123
    },
    "DOT": {
      "EUR": 0.123,
      "USD": 0.123
    },
    "ETH": {
      "EUR": 0.123,
      "USD": 0.123
    }
  },
  "success": true
}
```

[ [Table of Contents](#table-of-contents) ]
