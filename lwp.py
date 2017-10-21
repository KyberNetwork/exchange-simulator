# coding=utf-8
# lwp.py

from operator import itemgetter
import time
import requests

HOST = 'http://13.229.54.28:8000/prices'
VALID_HTTP_RESPONSE = [200]


class PriceType:
    """
    Emum for PriceType
    """
    ask = 'Ask'
    bid = 'Bid'


def current_timestamp():
    """
    Return current timestamp
    """
    return int(round(time.time() * 1000))


def get_knlw_prices(input_data):
    """
    Input:  List of pair of token and params
            Example:
            [{'BaseToken': 'OMG', 'DestToken': 'ETH', 'PriceType': PriceType.ask, 'RequiredQty': 1000, 'DateTimeStamp': 1508282098742},
             {'BaseToken': 'KNC', 'DestToken': 'ETH', 'PriceType': PriceType.bid, 'RequiredQty': 2000, 'DateTimeStamp': 1508282098742}]
    Return: List of( {BaseToken, DestToken, PriceType, AvailableQty,
                     Price, InjectedSpreadInBps, DateTimeStamp} )
            If pair token not supported the avaiableQty and Price will be set to 0
            Example:
            {'success': True, 'data': [{'BaseToken': 'OMG', 'DestToken': 'ETH',
                                        'PriceType': 'Ask', 'AvaiableQty': 1000,
                                        'InjectedSpreadInBps': 0,
                                        'Price': 0.025, 'DateTimeStamp': 1508282098742},
                                    {'BaseToken': 'KNC', 'DestToken': 'ETH',
                                        'PriceType': 'Ask', 'AvaiableQty': 2000,
                                        'InjectedSpreadInBps': 0,
                                        'Price': 0.002, 'DateTimeStamp': 1508282098742}]}
    """
    result = []
    market_data = get_market_data(HOST)
    if not market_data["success"]:
        return {"success": False, "reason": market_data["reason"]}
    for query in input_data:
        base_token = query['BaseToken']
        dest_token = query['DestToken']
        price_type = query['PriceType']
        required_qty = query['RequiredQty']
        if 'DateTimeStamp' in query:
            date_time_stamp = query['DateTimeStamp']
        else:
            date_time_stamp = current_timestamp()
        pair_data = get_pair_data(
            market_data, base_token, dest_token, price_type)
        injected_spread = get_injected_spread_in_bps()
        calculated_lwp, avaiable_quantity = calculate_lwp(
            pair_data, required_qty)
        lwp = (1 + (injected_spread / 10000)) * calculated_lwp
        result.append({'BaseToken': base_token, 'DestToken': dest_token,
                       'PriceType': price_type, 'AvaiableQty': avaiable_quantity,
                       'InjectedSpreadInBps': injected_spread,
                       'Price': lwp, 'DateTimeStamp': date_time_stamp})
    return {"success": True, "data": result}


def get_market_data(host):
    """
    Query all the data of all pair from supported exchanges
    """
    try:
        r = requests.get(host)
    except requests.exceptions.RequestException:
        return {"success": False, "reason": "Can not make request to host"}
    if r.status_code in VALID_HTTP_RESPONSE:
        market_data = r.json()
        if "success" in market_data and ("data" in market_data or "reason" in market_data):
            return market_data
        else:
            return {"success": False, "reason": "Invalid server data format"}
    return {"success": False, "reason": "Invalid server status code"}


def get_pair_data(market_data, base_token, dest_token, price_type):
    """
    Query the data of all avaiable exchanges of recent pair
    """
    pair_name = base_token + '-' + dest_token
    pair_name.capitalize()
    if pair_name in market_data["data"]:
        return parse_pair_data(market_data["data"][pair_name], price_type)
    else:
        return []


def parse_pair_data(pair_data, price_type):
    """
    Parse the pair data to calculate format
    Return result is sorted by price asc if is ask price, desc if is bid price
    """
    if(price_type == PriceType.bid):
        price_type_string = 'BuyPrices'
        reversed_sort = True
    else:
        price_type_string = 'SellPrices'
        reversed_sort = False
    data = []
    for exchange in pair_data:
        for command in pair_data[exchange][price_type_string]:
            data.append((command['Rate'], command['Quantity']))
    data.sort(key=itemgetter(0), reverse=reversed_sort)
    return data


def get_injected_spread_in_bps():
    """
    Query spread margin in BPS
    """
    # TODO: query the spread margin when have api, currently return 0
    return 0


def calculate_lwp(market_data, required_qty):
    """
    Calculate liquidity weighted price
    Input:  market_data - a sorted list of tube,
            first value in tube is price,
            second value is volume required_qty
    Output: liquidity weighted prce
            avaiable quantity
    """
    if(required_qty) <= 0:
        return 0, 0
    avaiable_quantity = 0
    required_market_deep = 0
    for a in market_data:
        price, volume = a
        needed_volume = required_qty - avaiable_quantity
        if needed_volume > volume:
            required_market_deep += price * volume
            avaiable_quantity += volume
        else:
            required_market_deep += price * needed_volume
            avaiable_quantity = required_qty
            break
    if avaiable_quantity > 0:
        lwp = required_market_deep / avaiable_quantity
    else:
        lwp = 0
    return lwp, avaiable_quantity