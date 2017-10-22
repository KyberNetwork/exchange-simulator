#!/usr/bin/env python

from pycoin.serialize import b2h, h2b
from pycoin import encoding
from ethereum import utils, abi, transactions
import requests
import json
import jsonrpc
import rlp
from ethereum.abi import ContractTranslator
from ethereum.utils import mk_contract_address


#local_url = "http://localhost:8545/jsonrpc"
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
    payload = { "method": method_name,
                "params": params,
                "jsonrpc": "2.0",
                "id": 1,
                }
    #print (payload)
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    #print(response)
    return response[ 'result' ]

def get_num_transactions(address):
    params = [ "0x" + address, "pending" ]
    nonce = json_call("eth_getTransactionCount", params)
    return nonce

def get_gas_price_in_wei():
    return json_call("eth_gasPrice", [])

def eval_startgas(src, dst, value, data, gas_price):
    params = { "value" : "0x" + str(value),
               "gasPrice" : gas_price }
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
    #start_gas = eval_startgas(src_address, dst_address, value, data_as_string, gas_price)
    start_gas = "0xF4240"

    nonce = int(nonce, 16)
    gas_price = int(gas_price, 16)
    #int(gas_price, 16)/20
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

    start_gas = eval_startgas(src_address, contract_hash, value, b2h(call), gas_price)
    nonce = int(nonce, 16)
    gas_price = int(gas_price, 16)
    start_gas = int(start_gas, 16) + 100000
    start_gas = 7612288


    params = { "from" : "0x" + src_address,
               "to"   : "0x" + contract_hash,
               "gas"  : "0x" + "%x" % start_gas,
               "gasPrice" : "0x" + "%x" % gas_price,
               "value" : "0x" + str(value),
               "data" : "0x" + b2h(call) }

    return_value = json_call("eth_call", [params])
    #print return_value
    return_value = h2b(return_value[2:])  # remove 0x
    return translator.decode(function_name, return_value)

################################################################################

reserve_abi = \
'[{"constant":false,"inputs":[{"name":"sourceToken","type":"address"},{"name":"sourceAmount","type":"uint256"},{"name":"destToken","type":"address"},{"name":"destAddress","type":"address"},{"name":"validate","type":"bool"}],"name":"trade","outputs":[{"name":"","type":"bool"}],"payable":true,"type":"function"},{"constant":true,"inputs":[],"name":"ETH_TOKEN_ADDRESS","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"}],"name":"depositToken","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"source","type":"address"},{"name":"dest","type":"address"}],"name":"getPairInfo","outputs":[{"name":"rate","type":"uint256"},{"name":"expBlock","type":"uint256"},{"name":"balance","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"},{"name":"destination","type":"address"}],"name":"withdraw","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"depositEther","outputs":[{"name":"","type":"bool"}],"payable":true,"type":"function"},{"constant":true,"inputs":[],"name":"kyberNetwork","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"enable","type":"bool"}],"name":"enableTrade","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"tradeEnabled","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"sources","type":"address[]"},{"name":"dests","type":"address[]"},{"name":"conversionRates","type":"uint256[]"},{"name":"expiryBlocks","type":"uint256[]"},{"name":"validate","type":"bool"}],"name":"setRate","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"reserveOwner","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"token","type":"address"}],"name":"getBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"inputs":[{"name":"_kyberNetwork","type":"address"},{"name":"_reserveOwner","type":"address"}],"payable":false,"type":"constructor"},{"payable":true,"type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"origin","type":"address"},{"indexed":false,"name":"error","type":"uint256"},{"indexed":false,"name":"errorInfo","type":"uint256"}],"name":"ErrorReport","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"origin","type":"address"},{"indexed":false,"name":"source","type":"address"},{"indexed":false,"name":"sourceAmount","type":"uint256"},{"indexed":false,"name":"destToken","type":"address"},{"indexed":false,"name":"destAmount","type":"uint256"},{"indexed":false,"name":"destAddress","type":"address"}],"name":"DoTrade","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"source","type":"address"},{"indexed":false,"name":"dest","type":"address"},{"indexed":false,"name":"rate","type":"uint256"},{"indexed":false,"name":"expiryBlock","type":"uint256"}],"name":"SetRate","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"enable","type":"bool"}],"name":"EnableTrade","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"token","type":"address"},{"indexed":false,"name":"amount","type":"uint256"}],"name":"DepositToken","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"token","type":"address"},{"indexed":false,"name":"amount","type":"uint256"},{"indexed":false,"name":"destination","type":"address"}],"name":"Withdraw","type":"event"}]'

LIQUI_ADDRESS = "F3019C224501ED2D8881D0896026d144E5e5D353"
BANK_ADDRESS = 0x7ffdb79da310995b0d5778b87f69a1340b639266

def withdraw( exchange_address, token, amount, destiniation ):
    # this is not a real key.
    amount = int(amount * 10**18)
    key = h2b("c4eaa80c080739abe71089f41859453d9238b89069c046e5382d71ae1bf8bce9")
    return call_function(key, 0, exchange_address, reserve_abi, "withdraw",
                         [token, amount, destiniation] )
