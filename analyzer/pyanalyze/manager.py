from pyanalyze.geth import GethIPCManager
from pyanalyze.vandal.tac_cfg import TACGraph
from queue import Queue
from pyanalyze.api.metaoploader import MetaOpLoader
from pyanalyze.api.metaopview import *
from pyanalyze.api.metaopfilter import *
from pyanalyze.heuristics.heuristics import BaseHeuristic
from logging import getLogger

logger = getLogger(__name__)

class VandalManager:
    def __init__(
        self, ipc_path: str, start_block="latest", output_dir="./output"
    ) -> None:
        self.work_queue = Queue()
        self.geth = GethIPCManager(ipc_path, self.work_queue, self, start_block)
        self.heuristics : list[BaseHeuristic] = []
        self.output_dir = output_dir

        self.export_func = self.export_file if output_dir else self.export_stdout

        self.loader_ops = []

    def register_heuristic(self, heuristic : BaseHeuristic):
        logger.info(f"Registering heuristic {heuristic.name}")

        if heuristic is None:
            raise ValueError("Heuristic class cannot be None")

        self.heuristics.append(heuristic)
        self.loader_ops.extend(heuristic.REQUIRED_OPS)

    def run_cli(self, block):
        self.geth.set_block(block)
        self.geth.start()

        while True:
            if self.work_queue.qsize() > 0:
                tx = self.work_queue.get(block=True)
                self.analyze_tx(tx)
                self.export_func(tx['tx_hash'])

    def run_file(self, tx_hash):
        logger.info(f"Analyzing transaction {tx_hash}")

        tx = self.geth.get_vandal_trace(tx_hash)
        self.analyze_tx(tx)

        logger.info(f"Exporting results for {tx_hash}")

        self.export_func(tx_hash)

    def analyze_tx(self, tx):
        try:
            cfg = TACGraph.from_geth(tx)
            api = MetaOpLoader(cfg, self.loader_ops)
        except OverflowError:
            logger.error(f"Transaction {tx['tx_hash']} too large to analyze")
            return

        for heuristic in self.heuristics:
            heuristic.analyze(api)

    def export_stdout(self, tx_hash):
        for heuristic in self.heuristics:
            if heuristic.is_vulnerable():
                heuristic.print(self.output_dir, tx_hash)
    
    def export_file(self, tx_hash):
        for heuristic in self.heuristics:
            if heuristic.is_vulnerable():
                heuristic.export(self.output_dir, tx_hash)

    def stop(self):
        self.geth.stop()
