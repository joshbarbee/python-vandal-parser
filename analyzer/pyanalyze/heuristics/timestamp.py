from pyanalyze.heuristics.heuristics import BaseHeuristic
from pyanalyze.api.metaopview import *
from pyanalyze.api.metaopfilter import *
from pyanalyze.api.metaop import TIMESTAMP, JUMPI

class TimestampDependency(BaseHeuristic):
    REQUIRED_OPS = [TIMESTAMP, JUMPI]

    def __init__(self):
        super().__init__('TimestampDependency')

    def analyze(self, api):
        timestamp : TIMESTAMPMetaOpView = api.get_ops("TIMESTAMP", filters = DiscreteFilters.depth_eq(1))
        jumpi : JUMPIMetaOpView = api.get_ops("JUMPI", filters = DiscreteFilters.depth_eq(1))

        if timestamp is None or jumpi is None:
            return
        
        timestamp.link(jumpi, Filters.OpIndexLT)
        timestamp.timestamp(OpAction.IS_DESCENDANT, jumpi.destination)

        self.results = timestamp.get_results()