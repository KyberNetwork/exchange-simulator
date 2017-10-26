#!/usr/bin/python3

from pycoin.serialize import b2h, h2b
from pycoin import encoding
from ethereum import utils, abi, transactions
import requests
import json
import jsonrpc
import rlp
from ethereum.abi import ContractTranslator
from ethereum.utils import mk_contract_address


# local_url = "http://localhost:8545/jsonrpc"
local_url = "https://kovan.infura.io"

def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z

def json_call(method_name, params):
    url = local_url
    headers = {'content-type': 'application/json'}
    # Example echo method
    payload = {"method": method_name,
               "params": params,
               "jsonrpc": "2.0",
               "id": 1,
               }
    # print (payload)
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()
    # print(response)
    return response['result']


def get_num_transactions(address):
    params = ["0x" + address, "pending"]
    nonce = json_call("eth_getTransactionCount", params)
    return nonce


def get_gas_price_in_wei():
    return json_call("eth_gasPrice", [])


def eval_startgas(src, dst, value, data, gas_price):
    params = {"value": "0x" + str(value),
              "gasPrice": gas_price}
    if len(data) > 0:
        params["data"] = "0x" + str(data)
    if len(dst) > 0:
        params["to"] = "0x" + dst

    return json_call("eth_estimateGas", [params])


def make_transaction(src_priv_key, dst_address, value, data):
    src_address = b2h(utils.privtoaddr(src_priv_key))
    nonce = get_num_transactions(src_address)
    gas_price = get_gas_price_in_wei()
    data_as_string = b2h(data)
    # print len(data_as_string)
    # if len(data) > 0:
    #    data_as_string = "0x" + data_as_string
    # start_gas = eval_startgas(src_address, dst_address, value,
    # data_as_string, gas_price)
    start_gas = "0xF4240"

    nonce = int(nonce, 16)
    gas_price = int(gas_price, 16)
    # int(gas_price, 16)/20
    start_gas = int(start_gas, 16) + 100000

    tx = transactions.Transaction(nonce,
                                  gas_price,
                                  start_gas,
                                  dst_address,
                                  value,
                                  data).sign(src_priv_key)

    tx_hex = b2h(rlp.encode(tx))
    tx_hash = b2h(tx.hash)

    params = ["0x" + tx_hex]
    return_value = json_call("eth_sendRawTransaction", params)
    if return_value == "0x0000000000000000000000000000000000000000000000000000000000000000":
        print ("Transaction failed")
        return return_value

    return return_value


def call_function(priv_key, value, contract_hash, contract_abi, function_name, args):
    translator = ContractTranslator(json.loads(contract_abi))
    call = translator.encode_function_call(function_name, args)
    return make_transaction(priv_key, contract_hash, value, call)


def call_const_function(priv_key, value, contract_hash, contract_abi, function_name, args):
    src_address = b2h(utils.privtoaddr(priv_key))
    translator = ContractTranslator(json.loads(contract_abi))
    call = translator.encode_function_call(function_name, args)
    nonce = get_num_transactions(src_address)
    gas_price = get_gas_price_in_wei()

    start_gas = eval_startgas(
        src_address, contract_hash, value, b2h(call), gas_price)
    nonce = int(nonce, 16)
    gas_price = int(gas_price, 16)
    start_gas = int(start_gas, 16) + 100000
    start_gas = 7612288

    params = {"from": "0x" + src_address,
              "to": "0x" + contract_hash,
              "gas": "0x" + "%x" % start_gas,
              "gasPrice": "0x" + "%x" % gas_price,
              "value": "0x" + str(value),
              "data": "0x" + b2h(call)}

    return_value = json_call("eth_call", [params])
    # print return_value
    return_value = h2b(return_value[2:])  # remove 0x
    return translator.decode_function_result(function_name, return_value)

#

reserve_abi = \
    '[{"constant":true,"inputs":[],"name":"ETH_TOKEN_ADDRESS","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"srcAmount","type":"uint256"},{"name":"dest","type":"address"},{"name":"destAmount","type":"uint256"}],"name":"convert","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"},{"name":"tokenAmount","type":"uint256"},{"name":"destination","type":"address"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"bank","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"depositEther","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"name":"tokens","type":"address[]"},{"name":"amounts","type":"uint256[]"}],"name":"clearBalances","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"exchange","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"token","type":"address"}],"name":"getBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_exchange","type":"string"},{"name":"_bank","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"payable":true,"stateMutability":"payable","type":"fallback"}]'

#

#


def to_hex_address(integer):
    return "%040x" % integer

#


def withdraw(exchange_address, token, amount, destiniation):
    # this is not a real key.
    key = h2b(
        "c4eaa80c080739abe71089f41859453d9238b89069c046e5382d71ae1bf8bce9")
    return call_function(
        key, 0, to_hex_address(exchange_address), reserve_abi, "withdraw",
                         [token, amount, destiniation])


#

def get_balances(exchange_address, tokens):
    # this is not a real key.
    key = h2b(
        "c4eaa80c080739abe71089f41859453d9238b89069c046e5382d71ae1bf8bce9")

    result = []

    for token in tokens:
        balance = call_const_function(
            key, 0, to_hex_address(exchange_address), reserve_abi, "getBalance",
                                      [token])[0]
        result = result + [balance]

    return result

#


def is_tx_confirmed(tx_hash):
    if(str(tx_hash).startswith("0x")):
        params = str(tx_hash)
    else:
        params = "0x" + tx_hash
    result = json_call("eth_getTransactionReceipt", [params])
    if(result is None):
        return False
    return not(result["blockHash"] is None)


#

def wait_for_tx_confirmation(tx_hash):
    round = 0
    while(not is_tx_confirmed(tx_hash)):
        round += 1
        if(round > 100):
            return False


#

def clear_deposits(exchange_address, token_array, amounts):
    # this is not a real key.
    key = h2b(
        "c4eaa80c080739abe71089f41859453d9238b89069c046e5382d71ae1bf8bce9")
    return call_function(
        key, 0, to_hex_address(exchange_address), reserve_abi, "clearBalances",
                         [token_array, amounts])
