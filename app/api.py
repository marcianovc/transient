from os import environ
from flask import Flask, jsonify, request, send_file
from app.database import db_session
from app.decorators import requires_basic_auth
from app import utils, setup, teardown


setup()
app = Flask(__name__)


def run():
    host = environ.get("HOST", "127.0.0.1")
    port = int(environ.get("PORT", 3000))
    debug = environ.get("DEBUG", False)
    app.run(host=host, port=port, debug=debug)


@app.route("/")
def hello():
    return "Sup?"


@app.route("/payments", methods=['POST'])
def create_payment():
    from app.payments import create_payment
    payment = create_payment(request.json, dump=True)
    return jsonify({
        'success': True,
        'payment': payment
    })


@app.route("/transactions", methods=['POST'])
def create_transaction():
    from app.payments import create_transaction
    transaction = create_transaction(request.json, dump=True)
    return jsonify({
        'success': True,
        'transaction': transaction
    })


@app.route("/payments/<payment_id>/qrcode.png", methods=['GET'])
def get_qrcode(payment_id):
    from app.payments import create_payment_qrcode
    image = get_payment_qrcode(payment_id)
    return utils.serve_pil_image(image, "png")


@app.teardown_appcontext
def shutdown_session(exception=None):
    teardown()
