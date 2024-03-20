from web3 import Web3
import json

w3 = Web3(Web3.IPCProvider('/tmp/geth.ipc'))

endpoint = 'debug_traceVandalTransaction'
TX = "0x715699e78ca8c777d42fccb5f15c5a4f3e4ddb253ba9063c556f22a61c24a79d"

res = w3.provider.make_request(endpoint, [TX])

with open('vandal.json', 'w') as f:
    json.dump(res, f, indent=4)