from pyanalyze.heuristics.heuristics import BaseHeuristic
from pyanalyze.api.metaopview import *
from pyanalyze.api.metaopfilter import *
from pyanalyze.api.metaop import CALL, JUMPI

class UncheckedCall(BaseHeuristic):
    REQUIRED_OPS = [CALL, JUMPI]

    def __init__(self):
        super().__init__('UncheckedCall')

    def analyze(self, api):
        call : CALLMetaOpView = api.get_ops("CALL", filters = DiscreteFilters.depth_eq(1))
        jumpi : JUMPIMetaOpView = api.get_ops("JUMPI", filters = DiscreteFilters.depth_eq(1))

        if call is None or jumpi is None:
            return
        
        call.link(jumpi, filters=[Filters.DepthEQ, Filters.CallIndexEQ])
        call.success(OpAction.IS_NOT_DESCENDANT, jumpi.destination)
        
        self.results = call.get_results()