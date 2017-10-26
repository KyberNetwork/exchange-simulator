#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import json

import exchange_api_interface
import exchange

app = Flask(__name__)
api = Api(app)


class LiquiTrade(Resource):

    def post(self, method):
        """A 'requests' dictionary is made that has the Post Request received
        in the web service and the appropriate parse """
        exchange_parser = exchange_api_interface.LiquiApiInterface()
        exchange_caller = exchange.Exchange()

        post_reqs = {
            "Trade": {
                "params_method": exchange_api_interface.TradeParams,
                "exchange_method": exchange_caller.execute_trade},
            "WithdrawCoin": {
                "params_method": exchange_api_interface.WithdrawParams,
                "exchange_method": exchange_caller.withdraw},
            "getInfo": {
                "params_method": exchange_api_interface.GetBalanceParams,
                "exchange_method": exchange_caller.get_user_balance}
            # "CancelOrder": {
            #    "params_method": exchange_api_interface.CancelTradeParams}
            #    "exchange_method":exchange_caller.==MISSING_METHOD==},
            # "ActiveOrders": ,
            # "OrderHistory":,
            # "OrderInfo":,
            # "TradeHistory":,

        }

        if "Key" not in request.headers:
            return jsonify({
                "success": 0,
                "error": "Missing 'Key' Header"
            })

        try:
            request_all = json.loads(request.data)
        except json.JSONDecodeError:
            return jsonify({
                "success": 0,
                "error": "Invalid data format in your request"
            })

        request_all["api_key"] = request.headers["key"]
        exchange_parser.parse_to_exchange(method, request_all)
        if "error" in exchange_parser.exchange_actions:
            return jsonify(exchange_parser.exchange_actions)
        else:
            exchange_params = post_reqs[method]["params_method"](
                **exchange_parser.exchange_actions)
            exchange_reply = (
                exchange_parser.parse_from_exchange(
                    method, post_reqs[method]["exchange_method"](
                        exchange_params)))
            return jsonify(exchange_reply)


api.add_resource(LiquiTrade, "/liqui/<method>")


if __name__ == "__main__":
    app.run(port="5002")
