#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import json
from enum import Enum

import exchange_api_interface

app = Flask(__name__)
api = Api(app)


class Employees(Resource):

    def get(self):
        return {'employees': 'zelda'}

    def post(self):
        print ("hello")
        print (request.args)


class LiquiTrade(Resource):

    def post(self):
        args = exchange_interface.LiquiApiInterface().prase_trade_args(
            request.args)
        if(args is None):
            raise ValueError('liqui trade args are in invalid format')


api.add_resource(Employees, '/employees')  # Route_1
api.add_resource(Employees2, '/bittrex/employees')  # Route_1
api.add_resource(Tracks, '/tracks')  # Route_2
api.add_resource(Employees_Name, '/employees/<employee_id>')  # Route_3


if __name__ == '__main__':
    app.run(port='5002')
