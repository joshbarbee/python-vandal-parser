from pyanalyze.heuristics.heuristics import BaseHeuristic
from pyanalyze.api.metaopview import *
from pyanalyze.api.metaopfilter import *
from pyanalyze.api.metaop import REVERT, CALL, JUMPI

class FailedSend(BaseHeuristic):
    REQUIRED_OPS = [REVERT, CALL, JUMPI]

    def __init__(self):
        super().__init__('FailedSend')

    def analyze(self, api):
        revert : REVERTMetaOpView = api.get_ops("REVERT", filters = DiscreteFilters.depth_eq(1))
        call : CALLMetaOpView = api.get_ops("CALL", filters = DiscreteFilters.depth_eq(1))
        jumpi : JUMPIMetaOpView = api.get_ops("JUMPI", filters = DiscreteFilters.depth_eq(1))

        if revert is None or call is None or jumpi is None:
            return

        call.value(OpAction.IS_VALUE_NE, 0)
        call.success(OpAction.IS_VALUE_EQ, 0)

        jumpi.link(revert, Filters.OpIndexLT)
        jumpi.link(call, Filters.OpIndexGT)

        jumpi.condition(OpAction.IS_DESCENDANT, call.success)

        self.results = jumpi.get_results()