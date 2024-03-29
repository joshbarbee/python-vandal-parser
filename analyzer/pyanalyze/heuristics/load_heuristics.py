# attempt to find heuristic files from provided directory
import os
from glob import glob

from pyanalyze.heuristics.heuristics import BaseHeuristic
from pyanalyze.heuristics.reentrancy import Reentrancy
from pyanalyze.heuristics.timestamp import TimestampDependency
from pyanalyze.heuristics.unchecked_call import UncheckedCall
from pyanalyze.heuristics.failed_send import FailedSend

INCLUDE_HEURISTICS = {
    "reentrancy": Reentrancy,
    "timestamp": TimestampDependency,
    "unchecked_call": UncheckedCall,
    "failed_send": FailedSend
}

def load_heuristics(heuristic_dir):
    if heuristic_dir is None:
        return INCLUDE_HEURISTICS
    
    heuristics = INCLUDE_HEURISTICS.copy()

    for file in glob(os.path.join(os.path.dirname(os.path.abspath(__file__))), "*.py"):
        if file == "__init__.py":
            continue

        module = __import__(file)
        for name, obj in module.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, BaseHeuristic):
                heuristics[name] = obj

def get_heuristics(heuristic_name = None, heuristic_dir = None):
    heuristics = load_heuristics(heuristic_dir)

    if heuristic_name is None:
        return list(heuristics.values())

    many_heuristics = heuristic_name.split(",")
    
    res = []
    for heuristic in many_heuristics:
        heuristic_text = heuristic.strip()
        if heuristic_text not in heuristics:
            raise ValueError(f"Heuristic {heuristic} not found")
        res.append(heuristics[heuristic_text])

    return res