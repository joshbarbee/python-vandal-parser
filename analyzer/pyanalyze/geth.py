from web3 import Web3, exceptions
from queue import Queue
from threading import Thread
import time
import logging

logger = logging.getLogger(__name__)

class GethIPCManager:
    def __init__(
        self, ipc_path: str, output_queue: Queue, manager, start_block="latest"
    ) -> None:
        self.w3 = Web3(Web3.IPCProvider(ipc_path))
        self.tx_queue = Queue()
        self.output_queue = output_queue
        self.block = start_block
        self.manager = manager

        logger.info(f"Geth IPC Manager initialized with start block {self.block}")

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
        self.block = res["number"] + 1

        for tx in res["transactions"]:
            self.tx_queue.put(tx.hex())

    def get_vandal_trace(self, tx_hash: str) -> dict:
        endpoint = "debug_traceVandalTransaction"
        res = self.w3.provider.make_request(endpoint, [tx_hash])
        return res["result"]        

    def poll_for_txs(self):
        backoff = 1

        last_n_blocks = 0
        since_last_n = 0

        while True:
            try:
                res = self.w3.eth.get_block(self.block, full_transactions=False)
            except exceptions.BlockNotFound:
                logger.warning(
                    f"Block {self.block} not found. Retrying in {2**backoff} seconds"
                )

                if backoff > 10:
                    logger.error(
                        f"Block {self.block} not found after {backoff} retries. Exiting..."
                    )
                    break

                time.sleep(2**backoff)
                backoff += 1
                continue

            self.block += 1

            last_n_blocks += len(res["transactions"])
            since_last_n += 1

            if since_last_n == 1000:
                logger.info(
                    f"Found {last_n_blocks} transactions in the last 100 blocks"
                )
                last_n_blocks = 0
                since_last_n = 0

            for tx in res["transactions"]:
                self.tx_queue.put(tx.hex())

        self.manager.stop()

    def run(self):
        while True:
            if self.tx_queue.qsize() > 0:
                tx_hash = self.tx_queue.get(block=True)
                res = self.get_vandal_trace(tx_hash)
                if len(res) == 0:
                    continue
                res['tx_hash'] = tx_hash
                if res['Ops'] is not None:
                    self.output_queue.put(res)

    def stop(self):
        self.poll_thread.join()
        self.run_thread.join()