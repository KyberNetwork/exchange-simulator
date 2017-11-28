# exchange-simulator

A simulator of centeralized exchange.
Includes deposit and withdrawal of funds, and orders execution.

## Setup
```
pip install -r requirements.txt
```
## Usage
Open api for exchanges:
```sh
$ uwsgi --emperor *.ini
```
In **simulation** mode, import the data first:
```
$ python import_simulation_data.py & uwsgi --emperor *.ini
```
### Mode
Setup modes via KYBER_ENV variable: 

* **dev** is local development env **[DEFAULT]**
* **simulation** is with our market data and fake blockchain
* **kovan** deploy on a server to run with kovan
* **production** is mainnet