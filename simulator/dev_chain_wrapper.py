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

from simulator import utils as simulator_utils


logger = simulator_utils.get_logger('dev_chain_wrapper')


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
    logger.info('Real blockchain response: {}'.format(response))
    return response

#


class PendingTx:

    def __init__(self, raw_tx, tx_hash, current_timestamp):
        self.raw_tx = raw_tx
        self.tx_hash = tx_hash
        self.submission_time = current_timestamp


pending_txs = set()
current_rpc_id = 1024 * 1024 * 1024
confirmation_delay_in_milis = 10 * 1000
use_delay = True
use_get_transaction_by_hash = False


def check_pending_txs(current_timestamp):
    global pending_txs
    global current_rpc_id

    txs_to_remove = []
    for tx in pending_txs:
        if(tx.submission_time + confirmation_delay_in_milis <= current_timestamp):
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
    return {"id": id, "jsonrpc": rpc_version, "result": "0x" + tx_hash}


def handle_getTransactionByHash(method_name, params, rpc_version, id):
    response = blockchain_json_call(method_name, params, rpc_version, id)
    if(response['result'] is not None):
        # tx already in parity client
        return response

    # check if it is in pending txs
    tx_hash = (params[0])[2:]  # chop 0x from the beginning
    for pending_tx in pending_txs:
        if pending_tx.tx_hash == tx_hash:
            # found tx
            return {"id": id, "jsonrpc": rpc_version, "result": {"hash": "0x" + tx_hash}}
    else:
        return {"id": id, "jsonrpc": rpc_version, "result": None}


@app.route('/', methods=['POST'])
def index():
    global use_delay
    global use_get_transaction_by_hash
    timestamp = simulator_utils.get_timestamp()
    check_pending_txs(timestamp)

    req = request.get_data().decode()
    logger.info('Request params to delay: {}'.format(req))
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
    if(method_name == "eth_sendTransaction" and use_delay):
        response = {"id": id, "jsonrpc": rpc_version,
                    "result": "unsuppoted command in delay mode"}
    elif(method_name == "eth_getTransactionByHash" and use_delay):
        if(use_get_transaction_by_hash):
            response = handle_getTransactionByHash(
                method_name, params, rpc_version, id)
        else:
            response = {"id": id, "jsonrpc": rpc_version,
                        "result": "unsuppoted command in delay mode"}
    elif(method_name == "eth_sendRawTransaction" and use_delay):
        response = handle_send_raw_tx(
            method_name, params, rpc_version, id, timestamp)
    elif(method_name == "enableDelay"):
        use_delay = True
        response = {"id": id, "jsonrpc": rpc_version, "result": "Ok"}
    elif(method_name == "enableGetTransactionByHash"):
        use_get_transaction_by_hash = True
        response = {"id": id, "jsonrpc": rpc_version, "result": "Ok"}
    else:
        response = blockchain_json_call(method_name, params, rpc_version, id)
    if(output_is_array):
        response = [response]
    logger.info('Delay response: {}'.format(response))
    # print(str(response))
    return json.dumps(response)


if __name__ == '__main__':
    app.run()
