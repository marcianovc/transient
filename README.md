# Transient

[![Build Status](https://travis-ci.org/smilledge/transient.svg)](https://travis-ci.org/smilledge/transient)

Transient is a simple cryptocurrency (currently only Dogecoin) payment gateway. It is designed to be used as an external service, and not integrated directly into applications.

**This project is still in development and is not ready for use in production.**

## Install

```
git clone ...
pip install -r requirements.txt
cp .env.example .env # Update configuration options...
alembic upgrade head
python runserver.py
```

## Configure

Configuration should be supplied via environment variables (will be loaded using [python-dotenv](https://github.com/theskumar/python-dotenv)). `.env.example` provides a template with all available configuration options. This file should be copied to `.env` in the project root directory.

### walletnotify and blocknotify

You should update your cryptocurrency [configuration files](https://en.bitcoin.it/wiki/Running_Bitcoin#Bitcoin.conf_Configuration_File) (Eg. `~/.dogecoin/dogecoin.conf`) with the following values (be sure to update the currency code and script path).

```
blocknotify=/var/www/transient/notify_block.py DOGE %s
walletnotify=/var/www/transient/notify_transaction.py DOGE %s
```

These are used to notify Transient of incoming transactions or blocks.

## HTTP API

### (GET) /payments/:payment_id

Returns a payment resource by ID. See below for an example for the resoponse data for a payment.

### (GET) /payments/:payment_id/qrcode.png

Generates a QR Code PNG image for the payments crypto address.

### (POST) /payments
Create a new payment resource

**Example request body:**
```
{
    "currency": "DOGE",
    "amount": 10,
    "account": "DFq66AjLeoJTtpHo47fg3rYrUydZxcANLN"
}
```

**Example response body:**
```
{
    "success": true,
    "payment":{
        "id": "cdb849b5-ed04-4426-acac-a3c1bdd0f83e",
        "currency": "DOGE",
        "status": "UNPAID",
        "amount": 10,
        "amount_recieved": 0,
        "payment_address": "DFq66AjLeoJTtpHo47fg3rYrUydZxcANLN",
        "transactions": [],
        "created_at": "2015-11-29T02:47:18.291901+00:00",
        "updated_at": "2015-11-29T02:47:18.291901+00:00",
        "expires_at": null
    }
}
```

### Payment Status Webhook

You can receive notifications of payment status changes by adding a callback URL to the `PAYMENT_WEBHOOK_URL` configuration option.

When the status of a payment changes, Transient will make a POST request to the provided URL with the following data.

```
{
    "payment_id": "cdb849b5-ed04-4426-acac-a3c1bdd0f83e",
    "status": "PAID"
}
```

## AMQP API

TODO

## CLI API

TODO

## TODO
 - Make integration tests suck less
 - Find a way to test against coind servers without mocking
 - Handle under and over payments
 - Handle large volumes from walletnotify
 - Add optional AMQP API
 - Ability to customize the size and style of QR Codes
 - Allow payments to have an expiry date
 - Add support for Bitcoin and Litecoin
