#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import json

import exchange_api_interface
import exchange
from constants import LIQUI_API_KEY

app = Flask(__name__)
api = Api(app)


class Employees(Resource):
    def get(self):
        return {'employees': 'zelda'}

    def post(self):
        return jsonify({'test': True})


class LiquiTrade(Resource):

    def post(self, method):

        exmethod = exchange_api_interface.LiquiApiInterface()
        # ex = exchange.Exchange()

        if 'Key' not in request.headers:
            return jsonify({
                "success": 0,
                "error": "Missing 'Key' Header"
            })
        elif 'Key' in request.headers and (
                LIQUI_API_KEY != request.headers['Key']):
            return jsonify({
                "success": 0,
                "error": "Invalid api_key in  'Key' Header"
            })

        try:
            request_all = json.loads(request.data)
        except json.JSONDecodeError:
            return jsonify({
                "success": 0,
                "error": "Invalid data format in your request"
            })


        request_all['api_key'] = request.headers['key']
        exmethod.parse_method(method, request_all)
        if 'error' in exmethod.exchange_actions:
            return jsonify(exmethod.exchange_actions['errormsg'])
        else:
            method = method.lower()
            if method == 'trade':
                exchange_params = exchange_api_interface.TradeParams(
                    **exmethod.exchange_actions)
                # ex.execute_trade(exchange_params)
                return jsonify(vars(exchange_params))

            elif method == 'withdrawcoin':
                exchange_params = exchange_api_interface.WithdrawParams(
                    **exmethod.exchange_actions)
                # ex.withdraw(exchange_params)
                return jsonify(vars(exchange_params))

            elif method == 'getinfo':
                exchange_params = exchange_api_interface.GetBalanceParams(
                    **exmethod.exchange_actions)
                # ex.get_user_balance(exchange_params)
                return jsonify(vars(exchange_params))

            elif method == 'cancelorder':
                exchange_params = exchange_api_interface.CancelTradeParams(
                    **exmethod.exchange_actions)
                # ex.cancel_trade(exchange_params)
                return jsonify(vars(exchange_params))

            elif method == 'activeorders':
                exchange_params = exchange_api_interface.GetOrders_Open_Params(
                    **exmethod.exchange_actions)
                # ex.get_orders_allopen(exchange_params)
                return jsonify(vars(exchange_params))

            elif method == 'orderinfo':
                exchange_params = exchange_api_interface.GetOrder_Single_Params(
                    **exmethod.exchange_actions)
                # ex.get_order_single(exchange_params)
                return jsonify(vars(exchange_params))

            elif method == 'tradehistory':
                exchange_params = exchange_api_interface.GetHistoryParams(
                    **exmethod.exchange_actions)
                # ex.get_trade_history(exchange_params)
                return jsonify(vars(exchange_params))



api.add_resource(Employees, '/employees')  # Route_1
api.add_resource(LiquiTrade, '/liqui/<method>')
# api.add_resource(Employees2, '/bittrex/employees') # Route_1
# api.add_resource(Tracks, '/tracks') # Route_2
# api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3


if __name__ == '__main__':
    app.run(port='5002')
