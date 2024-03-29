from pyanalyze.api.metaopview import MetaOpResults
import json

class BaseHeuristic:
    REQUIRED_OPS = []
    OUTPUT_KEYS = []

    def __init__(self, name):
        self.name = name
        self.results : MetaOpResults = None

    def analyze(self, api):
        pass

    def export(self, output_dir, tx_hash):
        with open(f'{output_dir}/reentrancy-{tx_hash}.json', 'w') as f:
            json.dump(f, self.results)

    def is_vulnerable(self):
        return self.results is not None and len(self.results) > 0
        
    def print(self, tx_hash):
        print(f'Found vulnerable: {tx_hash} from {self.name} heuristic')
        if self.results is not None:
            self.results.print()