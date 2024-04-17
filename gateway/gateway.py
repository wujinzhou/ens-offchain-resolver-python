from time import time
import logging
from flask import Flask, jsonify, request
from dotenv import dotenv_values
import ssl
from resolver import Resolver
from database import Database
from eth_abi.abi import encode
import eth_keys
import json
from utils import remove_0x, make_message_hash

config = dotenv_values(".env")

context = ssl.SSLContext()
context.load_cert_chain(
    "/etc/letsencrypt/live/extranonce.ddnsfree.com/fullchain.pem",
    "/etc/letsencrypt/live/extranonce.ddnsfree.com/privkey.pem",
)

APP_NAME = "ens-offchain-gateway"
VERSION = "0.1.0"

DATABASE_FILE = "userdata.json"

database_instance = Database(DATABASE_FILE)
reslover = Resolver(database_instance)

# Set up logging
logging.basicConfig(
    filename=APP_NAME + ".log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)

app = Flask(APP_NAME)


# Root endpoint
@app.route("/", methods=["GET"])
def root():
    response = {
        "date": int(time()),  # Current UNIX epoch time
        "version": VERSION,  # Assume this is the actual version
        "name": APP_NAME,
    }
    return jsonify(response)


# Reslove ens request
@app.route("/lookup/<path:from_sender>", methods=["POST"])
def ens_reslove(from_sender):
    try:
        payload = json.loads(request.data)
        logging.info(f"request: {payload}")
        sender = payload["sender"]
        calldata = payload["data"]
        result = reslover.resolve(calldata)
        expiry = int(time()) + 60

        message_hash = make_message_hash(
            sender,
            expiry,
            bytes.fromhex(remove_0x(calldata)),
            result,
        )

        signer = eth_keys.keys.PrivateKey(bytes.fromhex(config["SIGNER_KEY"][2:]))
        signature = signer.sign_msg_hash(message_hash)
        (v, r, s) = signature.vrs
        # the `v` value to be either 27 or 28.
        v += 27

        sig = bytes.fromhex("".join(["%064x" % r, "%064x" % s, "%x" % v]))

        retdata = encode(["bytes", "uint64", "bytes"], [result, expiry, sig])
        response = {"data": "".join(["0x", retdata.hex()])}
        logging.info(
            f"response: {response} [message_hash] {message_hash.hex()} [sig] {sig.hex()}"
        )
        return jsonify(response)

    except Exception as e:
        if isinstance(e, NotImplementedError):
            logging.info("Not implemented")
        else:
            logging.error(f"Exception: {e} reslove: {from_sender} data: {request.data}")
        return jsonify({"message": "Error when handling request"}), 500


# Overwrite the default 404 handler
@app.errorhandler(404)
def not_found(e):
    # defining function
    return jsonify({"message": "The endpoint is not found ¯\\_(ツ)_/¯"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=config["SERVER_PORT"], ssl_context=context)
