from pyanalyze.heuristics.heuristics import BaseHeuristic
from pyanalyze.api.metaopview import *
from pyanalyze.api.metaopfilter import *
from pyanalyze.api.metaop import SLOAD, JUMPI, SSTORE

class Reentrancy(BaseHeuristic):
    REQUIRED_OPS = [SLOAD, JUMPI, SSTORE]
    OUTPUT_KEYS = [
        "SLOAD.op_index",
        "JUMPI.op_index",
        "SLOAD.depth",
        "SLOAD.call_index",
        "SSTORE.op_index",
        "SSTORE.call_number",
        "SSTORE.address",
        "SLOAD.address"
    ]

    def __init__(self):
        super().__init__('Reentrancy')

        self.sstore_depth_filter = OpFilter(
            operator=lambda sload, sstore: sload >= sstore + 2, attribute="depth"
        )

    def analyze(self, api):
        SLOAD : SLOADMetaOpView = api.get_ops("SLOAD", filters=DiscreteFilters.depth_gt(2))

        if SLOAD is None:
            return

        JUMPI : JUMPIMetaOpView = api.get_ops("JUMPI")

        if JUMPI is None:
            return
        
        SLOAD.link(JUMPI, filters=[Filters.CallIndexEQ, Filters.DepthEQ])
        SLOAD.value(action=OpAction.IS_DESCENDANT, on=JUMPI.destination)

        SSTORE : SSTOREMetaOpView = api.get_ops("SSTORE")

        if SSTORE is None:
            return

        SLOAD.link(SSTORE, filters=[self.sstore_depth_filter, Filters.OpIndexLT])

        SLOAD.key(action=OpAction.IS_VALUE_EQ, on=SSTORE.key)
        SLOAD.source_address(action=OpAction.IS_ADDRESS_EQ)

        self.results = SLOAD.get_results(self.OUTPUT_KEYS)