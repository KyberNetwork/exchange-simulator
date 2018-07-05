import os
import time


SOCKET_PATH = '/tmp/'
ALL_APP = ['binance', 'huobi', 'bittrex',
           'digix', 'forge', 'gdax', 'gemini', 'kraken']
TIMEOUT = 30
INTERVAL = 1


def all_app_awake():
    app_awake = 0
    for app in ALL_APP:
        socket_path = f'{SOCKET_PATH}/{app}.sock'
        if os.path.exists(socket_path):
            app_awake += 1

    print('Wait for all simulate endpoint ...')
    return app_awake == len(ALL_APP)


wait = 0
while wait < TIMEOUT:
    time.sleep(INTERVAL)
    wait += INTERVAL

    if all_app_awake():
        os._exit(0)

os._exit(1)
