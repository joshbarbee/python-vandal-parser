# simply runs on a given tx hash, used for testing / debugging
# tx is DAO hack

# required for any script outside of pyanalyze module

import sys
from os.path import abspath, dirname, join
import os

sys.path.insert(0, join(dirname(abspath(__file__)), ".."))

from pyanalyze.manager import VandalManager
from pyanalyze.heuristics.reentrancy import Reentrancy

os.makedirs("output", exist_ok=True)

# DAO hack
TX = "0x37085f336b5d3e588e37674544678f8cb0fc092a6de5d83bd647e20e5232897b"

manager = VandalManager("/tmp/geth.ipc")
manager.register_heuristic(Reentrancy())
manager.run_file(TX)
