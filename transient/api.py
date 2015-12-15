from os import environ
from flask import Flask, jsonify, request, send_file
from transient.lib.database import session


app = Flask(__name__)


def run():
    host = environ.get("HOST", "127.0.0.1")
    port = int(environ.get("PORT", 3000))
    debug = environ.get("DEBUG", False)
    app.run(host=host, port=port, debug=debug)


@app.route("/")
def get_root():
    return "Sup?"


@app.route("/ping")
def get_ping():
    return "pong"


@app.route("/payments", methods=['POST'])
def post_payment():
    from transient.services.payments import create_payment
    try:
        payment = create_payment(**request.json)
        session.add(payment)
        session.commit()
    except:
        session.rollback()
        return jsonify({
            'success': False
        })
    else:
        return jsonify({
            'success': True,
            'payment': payment.to_dict()
        })
    finally:
        session.remove()


@app.route("/transactions", methods=['POST'])
def post_transaction():
    from transient.services.transactions import create_transaction
    try:
        transaction = create_transaction(**request.json)
        session.add(transaction)
        session.commit()
    except Exception, e:
        session.rollback()
        return jsonify({
            'success': False
        })
    else:
        return jsonify({
            'success': True,
            'transaction': transaction.to_dict()
        })
    finally:
        session.remove()


@app.route("/payments/<payment_id>/qrcode.png", methods=['GET'])
def get_qrcode(payment_id):
    from transient.services.payments import get_payment_qrcode
    image = get_payment_qrcode(payment_id)
    return serve_pil_image(image, "png")


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


def serve_pil_image(pil_img, img_format="jpeg"):
    from StringIO import StringIO
    img_io = StringIO()
    pil_img.save(img_io, img_format.upper())
    img_io.seek(0)
    return send_file(img_io, mimetype='image/%s' % (img_format.lower()))
