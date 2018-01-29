#!/usr/bin/python3

import requests
import json
import jsonrpc
import rlp
import time

from flask import Flask, request, jsonify, Response

from pycoin.serialize import b2h, h2b
from pycoin import encoding
from ethereum import utils, abi, transactions
from ethereum.abi import ContractTranslator
from ethereum.utils import mk_contract_address


app = Flask(__name__)


local_url = "http://blockchain:8545/jsonrpc"


def blockchain_json_call(method_name, params, rpc_version, id):
    url = local_url
    headers = {'content-type': 'application/json'}
    # Example echo method
    payload = {"method": method_name,
               "params": params,
               "jsonrpc": rpc_version,
               "id": id,
               }
    # print (payload)
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()
    # print(response)
    print(str(response))
    return response

#


class PendingTx:

    def __init__(self, raw_tx, tx_hash, current_timestamp):
        self.raw_tx = raw_tx
        self.tx_hash = tx_hash
        self.submission_time = current_timestamp


pending_txs = set()
current_rpc_id = 1024 * 1024 * 1024
confirmation_delay_in_sec = 5
use_delay = False


def check_pending_txs(current_timestamp):
    global pending_txs
    global current_rpc_id

    txs_to_remove = []
    for tx in pending_txs:
        if(tx.submission_time + confirmation_delay_in_sec <= current_timestamp):
            params = [tx.raw_tx]
            blockchain_json_call(
                "eth_sendRawTransaction", params, "2.0", str(current_rpc_id))
            current_rpc_id += 1

            txs_to_remove.append(tx)

    for tx in txs_to_remove:
        pending_txs.remove(tx)


def handle_send_raw_tx(method_name, params, rpc_version, id, current_timestamp):
    global pending_txs
    raw_tx = params[0]
    tx_hash = b2h(utils.sha3(h2b(raw_tx[2:])))
    pending_txs.add(PendingTx(raw_tx, tx_hash, current_timestamp))
    return {"id": id, "jsonrpc": rpc_version, "result": tx_hash}


@app.route('/', methods=['POST'])
def index():
    global use_delay
    timestamp = int(time.time())
    check_pending_txs(timestamp)

    req = request.get_data().decode()
    print(str(req))
    json_req = json.loads(req)
    output_is_array = False
    if (len(json_req) == 1):
        json_req = json_req[0]
        output_is_array = True
        print(str(json_req))
    method_name = json_req["method"]
    params = json_req["params"]
    rpc_version = json_req["jsonrpc"]
    id = json_req["id"]

    # some commands are not supported in delay mode
    if((method_name == "eth_sendTransaction" or
            method_name == "eth_getTransactionByHash") and use_delay):
        respone = {"id": id, "jsonrpc": rpc_version,
                   "result": "unsuppoted command in delay mode"}
    elif(method_name == "eth_sendRawTransaction" and use_delay):
        response = handle_send_raw_tx(
            method_name, params, rpc_version, id, timestamp)
    elif(method_name == "enableDelay"):
        use_delay = True
        response = {"id": id, "jsonrpc": rpc_version, "result": "Ok"}
    else:
        response = blockchain_json_call(method_name, params, rpc_version, id)
    if(output_is_array):
        response = [response]
    print(str(response))
    return json.dumps(response)


if __name__ == '__main__':
    app.run()
