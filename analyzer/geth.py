from web3 import Web3, exceptions
from queue import Queue
from threading import Thread
import time

class GethIPCManager():
    def __init__(self, ipc_path: str, output_queue : Queue, start_block = 'latest') -> None:
        self.w3 = Web3(Web3.IPCProvider(ipc_path))
        self.tx_queue = Queue()
        self.output_queue = output_queue
        self.block = start_block

    def set_block(self, block: str):
        self.block = block

    def start(self):
        self.__init_tx_queue()

        self.poll_thread = Thread(target=self.poll_for_txs)
        self.poll_thread.start()

        self.run_thread = Thread(target=self.run)
        self.run_thread.start()

    def __init_tx_queue(self):
        res = self.w3.eth.get_block(self.block, full_transactions=False)
        self.block = res['number'] + 1

        for tx in res['transactions']:
            self.tx_queue.put(tx.hex())
    
    def get_vandal_trace(self, tx_hash: str) -> dict:
        endpoint = 'debug_traceVandalTransaction'
        res = self.w3.provider.make_request(endpoint, [tx_hash])
        return res
    
    def poll_for_txs(self):
        backoff = 1

        while True:
            try:
                res = self.w3.eth.get_block(self.block, full_transactions=False)
            except exceptions.BlockNotFound:
                time.sleep(2**backoff)
                backoff += 1
                continue

            self.block += 1

            for tx in res['transactions']:
                self.tx_queue.put(tx.hex())
    
    def run(self):
        while True:
            if self.tx_queue.qsize() > 0:
                tx_hash = self.tx_queue.get(block = True)
                res = self.get_vandal_trace(tx_hash)

                if len(res['result']) == 0:
                    continue

                print('found one ', tx_hash)

                self.output_queue.put(res['result'])    
                
    def stop(self):
        self.poll_thread.join()
        self.run_thread.join()

GethIPCManager('/tmp/geth.ipc', Queue())