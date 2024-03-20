from analyzer.geth import GethIPCManager
from analyzer.vandal.tac_cfg import TACGraph
from queue import Queue
import argparse

class VandalManager():
    def __init__(self, ipc_path: str, start_block = 'latest', output_dir = './output') -> None:
        self.work_queue = Queue()
        self.geth = GethIPCManager(ipc_path, self.work_queue, start_block)
        self.heuristics = []
        self.output_dir = output_dir

    def register_heuristic(self, heuristic, config = {}):
        self.heuristics.append(heuristic(config))
        
    def run_cli(self, block):
        self.geth.set_block(block)
        self.geth.start()

        while True:
            if self.work_queue.qsize() > 0:
                tx = self.work_queue.get(block = True)
                self.analyze_tx(tx)

    def run_file(self, tx, heuristic = None):
        self.geth.get_vandal_trace(tx)
        self.analyze_tx(tx)

    def analyze_tx(self, tx):
        cfg = TACGraph.from_trace(tx)
        for heuristic in self.heuristics:
            heuristic.analyze(cfg)
            heuristic.export(self.output_dir)
        
    def stop(self):
        self.geth.stop()
            
