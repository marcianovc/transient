from os import environ
from flask import Flask, jsonify, request, send_file
from transient import setup, teardown


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
    from transient.services.payments import create_payment
    payment = create_payment(**request.json)
    return jsonify({
        'success': True,
        'payment': payment.to_dict()
    })


@app.route("/transactions", methods=['POST'])
def create_transaction():
    from transient.services.transactions import create_transaction
    transaction = create_transaction(**request.json)
    return jsonify({
        'success': True,
        'transaction': transaction.to_dict()
    })


@app.route("/payments/<payment_id>/qrcode.png", methods=['GET'])
def get_qrcode(payment_id):
    from transient.services.payments import get_payment_qrcode
    image = get_payment_qrcode(payment_id)
    return serve_pil_image(image, "png")


@app.teardown_appcontext
def shutdown_session(exception=None):
    teardown()


def serve_pil_image(pil_img, format="jpeg"):
    from StringIO import StringIO
    img_io = StringIO()
    pil_img.save(img_io, format.upper())
    img_io.seek(0)
    return send_file(img_io, mimetype='image/%s' % (format.lower()))
