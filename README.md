# exchange-simulator

A simulator of centeralized exchange.
Includes deposit and withdrawal of funds, and orders execution.

## Usage
```sh
$ python restful_api.py
```
Running in simulation mode
```sh
$ KYBER_ENV=simulation python restful_api.py
```

### Mode
Setup modes via KYBER_ENV variable: 

* **dev** is local development env **[DEFAULT]**
* **simulation** is with our market data and fake blockchain
* **kovan** deploy on a server to run with kovan
* **production** is mainnet

Running in the **simulation** mode requires to import the data market data first.