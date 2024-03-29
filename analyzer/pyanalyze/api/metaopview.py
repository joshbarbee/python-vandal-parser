import numpy as np
from typing import Union
from pyanalyze.api.metaop import MetaOp
from pyanalyze.api.metaconsts import *
from pyanalyze.api.metavariable import MetaVariable
import pprint
from pyanalyze.api.metaopfilter import OpFilter
import itertools

class MetaOpLink:
    def __init__(self, op: MetaOp):
        self.op = op
        self.links = []

    def add_link(self, link):
        self.links.append(link)

    def remove_link(self, link):
        self.links.remove(link)

    def is_empty(self):
        return len(self.links) == 0
    
class MetaOpDict:
    def __init__(self, ops):
        self._dict = {}
        self._init_dict(ops)

    def _init_dict(self, ops):
        for op in ops:
            self._dict[op] = {}

    def add_link(self, op, link_op, link):
        if link_op not in self._dict[op]:
            self._dict[op][link_op] = MetaOpLink(op)
            
        self._dict[op][link_op].add_link(link)

    def get_link(self, op, link_op):
        return self._dict[op][link_op]
    
    def get_all_links(self, op):
        return self._dict[op]
    
class MetaOpResult:
    def __init__(self, op):
        self.op = op
        self.rows : list[list[MetaOp]] = []

    def add_row(self, row):
        self.rows.append(row)

    def print(self):
        print(self.op)

    def print_keyed(self, keys):
        results = []
        for row in self.rows:
            res = {}
            SLOAD, JUMPI
            SLOAD, JUMPI, SSTORE

            row_names = [r.__class__.__name__ for r in row]


            for key in keys:
                op_cls, op_attr = key.split('.')

class MetaOpResults:
    def __init__(self, keys) -> None:
        self.keys = keys
        self.results = []

    def add_result(self, result : MetaOpResult):
        self.results.append(result)

    def __len__(self):
        return len(self.results)
    
    def print(self):
        for result in self.results:
            result.print()

    def print_keyed(self):
        # for each MetaOp, look at rows and find keys from same class
        for result in self.results:
            result.print_keyed(self.keys)

class MetaOpView:
    def __init__(
        self, op_name, ops: list[MetaOp] = None, addresses: dict[int, str] = None
    ):
        self.op_name = op_name
        self.addresses: dict[int, str] = addresses if addresses is not None else {}

        self.working_set = np.ones((len(ops),), dtype=bool)
        self.ops = ops

        self.links : MetaOpDict = MetaOpDict(ops)
        self.current_link = None

    def merge(self, other: "MetaOpView", inclusive: bool = False):
        if self.working_set.shape[0] != other.working_set.shape[0]:
            raise ValueError(
                "Cannot merge MetaOpViews with different working set sizes. Ensure you \
                                are merging MetaOpViews of the same opcode"
            )

        if inclusive:
            self.working_set |= other.working_set
        else:
            self.working_set &= other.working_set

        return self

    def filter(self, filters: Union[list[OpFilter], OpFilter] = None):
        if filters is None:
            return self

        if not isinstance(filters, list):
            filters = [filters]

        if len(filters) == 0:
            return

        for op in self.ops:
            if not all(
                filter.operator(
                    getattr(op, filter.attribute), filter.value
                )
                for filter in filters
            ):
                self.working_set[op._op_ws_index] = False

        return self
    
    def source_address(self, action = OpAction, address : str = None):
        if action is not None:
            if action == OpAction.IS_ADDRESS_EQ:
                return self._filter_link_address(operator.eq)
            elif action == OpAction.IS_ADDRESS_NE:
                return self._filter_link_address(operator.ne)
        elif address is not None:
            return self._filter_address(address)
        return self
        
    def _filter_address(self, address):
        depths_at_addr = []

        for depth, addr in self.addresses.items():
            if addr == address:
                depths_at_addr.append(depth)

        for op in self.ops:
            if self.working_set[op._op_ws_index]:
                if op.depth not in depths_at_addr:
                    self.working_set[op._op_ws_index] = False

        return self
    
    def _filter_link_address(self, operator = None):
        for op in self.ops:
            if self.working_set[op._op_ws_index] == False:
                continue

            link_ops = self._get_current_links(op)

            removed_links = []

            for link_op in link_ops:
                if not operator(link_op.address, op.address):
                    removed_links.append(link_op)
            
            for link_op in removed_links:
                self._remove_current_link(op, link_op)

            if self._current_link_empty(op):
                self.working_set[op._op_ws_index] = False

        return self
    
    def _get_current_links(self, op):
        if self.current_link is None:
            raise ValueError("No current link. Must link with other MetaOpview before calling function")

        return self.links._dict[op][self.current_link].links
    
    def _remove_current_link(self, op, link):
        if self.current_link is None:
            raise ValueError("No current link. Must link with other MetaOpview before calling function")
        
        self.links._dict[op][self.current_link].remove_link(link)

    def _current_link_empty(self, op):
        if self.current_link is None:
            raise ValueError("No current link. Must link with other MetaOpview before calling function")
        
        return self.links._dict[op][self.current_link].is_empty()

    def link(
        self, other: "MetaOpView", filters: Union[list[OpFilter], OpFilter] = None
    ) -> "MetaOpView":
        # create 2d array of all possible combinations of the two np arrays
        # then apply the filters to the 2d array,
        if filters is None:
            filters = []

        if not isinstance(filters, list):
            filters = [filters]

        if len(filters) == 0:
            return self

        for op in self.ops:
            for link_op in other.ops:
                add = True
                for filter in filters:
                    if not filter.operator(
                        getattr(op, filter.attribute), getattr(link_op, filter.attribute)
                    ):
                        add = False
                        break
                if add:
                    self.links.add_link(op, other, link_op)
            if other not in self.links._dict[op] or self.links._dict[op][other].is_empty():
                self.working_set[op._op_ws_index] = False

        self.current_link = other

        return self

    def filter_link(self, filters: Union[list[OpFilter], OpFilter]):
        if not isinstance(filters, list):
            filters = [filters]

        if len(filters) == 0:
            return self
        
        if self.current_link is None:
            raise ValueError("No link to filter")

        for op in self.ops:
            link_ops = self.links[op].links

            for link_op in link_ops:
                if not all(
                    filter.operator(
                        getattr(op, filter.attribute), getattr(link_op, filter.attribute)
                    )
                    for filter in filters
                ):
                    self._remove_current_link(op, link_op)

            if self._current_link_empty(op):
                self.working_set[op._op_ws_index] = False

        return self

    def get_results(self, keys = []):
        # get working set of ops, all links for working set ops across current and previous links
        # how to determine which fields to export? - just return all, let user decide
        
        ws = self.get_working_set()
        results = MetaOpResults(keys)

        # for each instance of self, find all possible pairings with all existing links

        for op in ws:
            result = MetaOpResult(op)

            links = self.links.get_all_links(op)
            cartesian_map = itertools.product(links.values())
            
            for m in cartesian_map:
                result.add_row(m)
                    
            results.add_result(result)
        
        return results

    def _is_in(self, self_op, self_vars, link_ops, link_attr):
        removed_links = []
        for link_op in link_ops:
            for var in self_vars:
                if var == getattr(link_op, link_attr):
                    break
            else:
                removed_links.append(link_op)

        for link_op in removed_links:
            self._remove_current_link(self_op, link_op)

        return self._current_link_empty(self_op) == False
    
    def is_relation(self, self_attr, other_attr, relation, invert = False):
        for op in self.ops:
            if self.working_set[op._op_ws_index]:
                nodes = getattr(getattr(op, self_attr), relation)()

                link_ops = self._get_current_links(op)

                if invert:
                    if self._is_in(op, nodes, link_ops, other_attr):
                        self.working_set[op._op_ws_index] = False
                else:
                    if not self._is_in(op, nodes, link_ops, other_attr):
                        self.working_set[op._op_ws_index] = False

        return self

    def is_descendant(self, self_attr, other_attr, invert = False):
        return self.is_relation(self_attr, other_attr, "descendants", invert)
    
    def is_ancestor(self, self_attr, other_attr, invert = False):
        return self.is_relation(self_attr, other_attr, "ancestors", invert)
    
    def is_parent(self, self_attr, other_attr, invert = False):
        return self.is_relation(self_attr, other_attr, "parents", invert)
    
    def is_child(self, self_attr, other_attr, invert = False):
        return self.is_relation(self_attr, other_attr, "children", invert)
    
    def is_value_int(self, self_attr, value, operator):
        for op in self.ops:
            if self.working_set[op._op_ws_index]:
                attr = getattr(op, self_attr)
                if not isinstance(attr, int):
                    raise ValueError("Value must be an integer")
                if not operator(attr, value):
                    self.working_set[op._op_ws_index] = False
    
    def is_value(self, self_attr, other_attr, operator):
        if isinstance(other_attr, int):
            return self.is_value_int(self_attr, other_attr, operator)
        
        other_attr = other_attr()

        for op in self.ops:
            if self.working_set[op._op_ws_index]:
                link_ops = self._get_current_links(op)
                
                removed_links = []

                for link_op in link_ops:
                    if not operator(getattr(op, self_attr), getattr(link_op, other_attr)):
                        removed_links.append(link_op)

                for link_op in removed_links:
                    self._remove_current_link(op, link_op)

                if self._current_link_empty(op):
                    self.working_set[op._op_ws_index] = False

        return self

    # on is a reference to a property of some other metaop
    def take_action(self, self_attr, action : OpAction, other_attr):
        match action: 
            case OpAction.IS_DESCENDANT:
                return self.is_descendant(self_attr, other_attr(), False)
            case OpAction.IS_NOT_DESCENDANT:
                return self.is_descendant(self_attr, other_attr(), True)
            case OpAction.IS_ANCESTOR:
                return self.is_ancestor(self_attr, other_attr(), False)
            case OpAction.IS_NOT_ANCESTOR:
                return self.is_ancestor(self_attr, other_attr(), True)
            case OpAction.IS_CHILD:
                return self.is_child(self_attr, other_attr())
            case OpAction.IS_PARENT:
                return self.is_parent(self_attr, other_attr())
            case OpAction.IS_VALUE_EQ:
                return self.is_value(self_attr, other_attr, MetaVariable.value_eq)
            case OpAction.IS_VALUE_NE:
                return self.is_value(self_attr, other_attr, MetaVariable.value_ne)
            case OpAction.IS_VALUE_LT:
                return self.is_value(self_attr, other_attr, MetaVariable.value_lt)
            case OpAction.IS_VALUE_GT:
                return self.is_value(self_attr, other_attr, MetaVariable.value_gt)
            case OpAction.IS_VALUE_LE:
                return self.is_value(self_attr, other_attr, MetaVariable.value_lte)
            case OpAction.IS_VALUE_GE:
                return self.is_value(self_attr, other_attr, MetaVariable.value_gte)

        return self

    def get_working_set(self):
        return [op for i, op in enumerate(self.ops) if self.working_set[i]]


class UnaryMetaOpView(MetaOpView):
    def operand(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "operand"

        return self.take_action("operand", action, on)

    def result(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "result"

        return self.take_action("result", action, on)


class BinaryMetaOpView(MetaOpView):

    def left(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "left"

        return self.take_action("left", action, on)

    def right(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "right"

        return self.take_action("right", action, on)

    def result(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "result"

        return self.take_action("result", action, on)


class TernaryMetaOpView(MetaOpView):
    def first(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "first"

        return self.take_action("first", action, on)

    def second(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "second"

        return self.take_action("second", action, on)

    def third(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "third"

        return self.take_action("third", action, on)

    def result(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "result"

        return self.take_action("result", action, on)


class CONSTMetaOpView(MetaOpView): ...


class STOPMetaOpView(MetaOpView): ...


class ADDMetaOpView(BinaryMetaOpView): ...


class SUBMetaOpView(BinaryMetaOpView): ...


class MULMetaOpView(BinaryMetaOpView): ...


class DIVMetaOpView(BinaryMetaOpView): ...


class SDIVMetaOpView(BinaryMetaOpView): ...


class MODMetaOpView(BinaryMetaOpView): ...


class SMODMetaOpView(BinaryMetaOpView): ...


class ADDMODMetaOpView(TernaryMetaOpView): ...


class MULMODMetaOpView(TernaryMetaOpView): ...


class EXPMetaOpView(MetaOpView):
    def base(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "base"

        return self.take_action("base", action, on)

    def exponent(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "exponent"

        return self.take_action("exponent", action, on)

    def result(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "result"

        return self.take_action("result", action, on)


class SIGNEXTENDMetaOpView(BinaryMetaOpView): ...


class LTMetaOpView(BinaryMetaOpView): ...


class GTMetaOpView(BinaryMetaOpView): ...


class SLTMetaOpView(BinaryMetaOpView): ...


class SGTMetaOpView(BinaryMetaOpView): ...


class EQMetaOpView(BinaryMetaOpView): ...


class ISZEROMetaOpView(UnaryMetaOpView): ...


class ANDMetaOpView(BinaryMetaOpView): ...


class ORMetaOpView(BinaryMetaOpView): ...


class XORMetaOpView(BinaryMetaOpView): ...


class NOTMetaOpView(UnaryMetaOpView): ...


class BYTEMetaOpView(BinaryMetaOpView): ...


class SHLMetaOpView(BinaryMetaOpView): ...


class SHRMetaOpView(BinaryMetaOpView): ...


class SHA3MetaOpView(MetaOpView): ...


class ADDRESSMetaOpView(MetaOpView):
    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)


class BALANCEMetaOpView(MetaOpView):
    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)

    def balance(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "balance"

        return self.take_action("balance", action, on)


class ORIGINMetaOpView(MetaOpView):

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)


class CALLERMetaOpView(MetaOpView):

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)


class CALLVALUEMetaOpView(MetaOpView):

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class CALLDATALOADMetaOpView(UnaryMetaOpView):

    def index(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "index"

        return self.take_action("index", action, on)

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class CALLDATASIZEMetaOpView(MetaOpView):

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class CALLDATACOPYMetaOpView(MetaOpView):

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def data_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "data_offset"

        return self.take_action("data_offset", action, on)

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class CODESIZEMetaOpView(MetaOpView):

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class CODECOPYMetaOpView(MetaOpView):

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def data_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "data_offset"

        return self.take_action("data_offset", action, on)

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class GASPRICEMetaOpView(MetaOpView):

    def price(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "price"

        return self.take_action("price", action, on)


class EXTCODESIZEMetaOpView(MetaOpView):

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class EXTCODECOPYMetaOpView(MetaOpView):

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def data_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "data_offset"

        return self.take_action("data_offset", action, on)

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class RETURNDATASIZEMetaOpView(MetaOpView):

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class RETURNDATACOPYMetaOpView(MetaOpView):

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def data_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "data_offset"

        return self.take_action("data_offset", action, on)

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class EXTCODEHASHMetaOpView(MetaOpView):

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)

    def code_hash(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "code_hash"

        return self.take_action("code_hash", action, on)


class BLOCKHASHMetaOpView(UnaryMetaOpView):

    def block_number(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "block_number"

        return self.take_action("block_number", action, on)

    def block_hash(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "block_hash"

        return self.take_action("block_hash", action, on)


class COINBASEMetaOpView(MetaOpView):

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)


class TIMESTAMPMetaOpView(MetaOpView):

    def timestamp(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "timestamp"

        return self.take_action("timestamp", action, on)


class NUMBERMetaOpView(MetaOpView):

    def block_number(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "block_number"

        return self.take_action("block_number", action, on)


class DIFFICULTYMetaOpView(MetaOpView):

    def difficulty(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "difficulty"

        return self.take_action("difficulty", action, on)


class GASLIMITMetaOpView(MetaOpView):

    def gas_limit(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "gas_limit"

        return self.take_action("gas_limit", action, on)


class POPMetaOpView(UnaryMetaOpView):

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class MLOADMetaOpView(UnaryMetaOpView):

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class MSTOREMetaOpView(BinaryMetaOpView):

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class MSTORE8MetaOpView(BinaryMetaOpView):

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class SLOADMetaOpView(UnaryMetaOpView):

    def key(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "key"

        return self.take_action("key", action, on)

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class SSTOREMetaOpView(BinaryMetaOpView):

    def key(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "key"

        return self.take_action("key", action, on)

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class JUMPMetaOpView(UnaryMetaOpView):

    def destination(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "destination"

        return self.take_action("destination", action, on)


class JUMPIMetaOpView(BinaryMetaOpView):

    def condition(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "condition"

        return self.take_action("condition", action, on)

    def destination(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "destination"

        return self.take_action("destination", action, on)


class PCMetaOpView(MetaOpView):

    def pc_value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "pc_value"

        return self.take_action("pc_value", action, on)


class MSIZEMetaOpView(MetaOpView):

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class GASMetaOpView(MetaOpView):

    def gas_remaining(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "gas_remaining"

        return self.take_action("gas_remaining", action, on)


class JUMPDESTMetaOpView(MetaOpView): ...


class PUSHMetaOpView(UnaryMetaOpView):

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class DUPMetaOpView(UnaryMetaOpView):

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class SWAPMetaOpView(UnaryMetaOpView):

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)


class CREATEMetaOpView(MetaOpView):

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)


class CALLMetaOpView(MetaOpView):

    def gas(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "gas"

        return self.take_action("gas", action, on)

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)

    def in_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "in_offset"

        return self.take_action("in_offset", action, on)

    def in_size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "in_size"

        return self.take_action("in_size", action, on)

    def out_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "out_offset"

        return self.take_action("out_offset", action, on)

    def out_size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "out_size"

        return self.take_action("out_size", action, on)

    def success(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "success"

        return self.take_action("success", action, on)


class CALLCODEMetaOpView(MetaOpView):

    def gas(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "gas"

        return self.take_action("gas", action, on)

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)

    def in_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "in_offset"

        return self.take_action("in_offset", action, on)

    def in_size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "in_size"

        return self.take_action("in_size", action, on)

    def out_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "out_offset"

        return self.take_action("out_offset", action, on)

    def out_size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "out_size"

        return self.take_action("out_size", action, on)

    def success(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "success"

        return self.take_action("success", action, on)


class RETURNMetaOpView(MetaOpView):

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class DELEGATECALLMetaOpView(MetaOpView):

    def gas(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "gas"

        return self.take_action("gas", action, on)

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)

    def in_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "in_offset"

        return self.take_action("in_offset", action, on)

    def in_size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "in_size"

        return self.take_action("in_size", action, on)

    def out_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "out_offset"

        return self.take_action("out_offset", action, on)

    def out_size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "out_size"

        return self.take_action("out_size", action, on)

    def success(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "success"

        return self.take_action("success", action, on)


class CREATE2MetaOpView(MetaOpView):

    def value(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "value"

        return self.take_action("value", action, on)

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)

    def salt(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "salt"

        return self.take_action("salt", action, on)

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)


class STATICCALLMetaOpView(MetaOpView):

    def gas(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "gas"

        return self.take_action("gas", action, on)

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)

    def in_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "in_offset"

        return self.take_action("in_offset", action, on)

    def in_size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "in_size"

        return self.take_action("in_size", action, on)

    def out_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "out_offset"

        return self.take_action("out_offset", action, on)

    def out_size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "out_size"

        return self.take_action("out_size", action, on)

    def success(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "success"

        return self.take_action("success", action, on)


class REVERTMetaOpView(MetaOpView):

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)


class SELFDESTRUCTMetaOpView(MetaOpView):

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)


class LOGMetaOpView(MetaOpView):

    def source_address(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "address"

        return self.take_action("address", action, on)

    def mem_offset(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "mem_offset"

        return self.take_action("mem_offset", action, on)

    def size(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "size"

        return self.take_action("size", action, on)

    def topics(self, action: OpAction = None, on=None):
        if action is None or on is None:
            return "topics"

        return self.take_action("topics", action, on)


op_name_to_opview = {
    "STOP": STOPMetaOpView,
    "ADD": ADDMetaOpView,
    "MUL": MULMetaOpView,
    "SUB": SUBMetaOpView,
    "DIV": DIVMetaOpView,
    "SDIV": SDIVMetaOpView,
    "MOD": MODMetaOpView,
    "SMOD": SMODMetaOpView,
    "ADDMOD": ADDMODMetaOpView,
    "MULMOD": MULMODMetaOpView,
    "EXP": EXPMetaOpView,
    "SIGNEXTEND": SIGNEXTENDMetaOpView,
    "LT": LTMetaOpView,
    "GT": GTMetaOpView,
    "SLT": SLTMetaOpView,
    "SGT": SGTMetaOpView,
    "EQ": EQMetaOpView,
    "ISZERO": ISZEROMetaOpView,
    "AND": ANDMetaOpView,
    "OR": ORMetaOpView,
    "XOR": XORMetaOpView,
    "NOT": NOTMetaOpView,
    "BYTE": BYTEMetaOpView,
    "SHL": SHLMetaOpView,
    "SHR": SHRMetaOpView,
    "SHA3": SHA3MetaOpView,
    "KECCAK256": SHA3MetaOpView,
    "ADDRESS": ADDRESSMetaOpView,
    "BALANCE": BALANCEMetaOpView,
    "ORIGIN": ORIGINMetaOpView,
    "CALLER": CALLERMetaOpView,
    "CALLVALUE": CALLVALUEMetaOpView,
    "CALLDATALOAD": CALLDATALOADMetaOpView,
    "CALLDATASIZE": CALLDATASIZEMetaOpView,
    "CALLDATACOPY": CALLDATACOPYMetaOpView,
    "CODESIZE": CODESIZEMetaOpView,
    "CODECOPY": CODECOPYMetaOpView,
    "GASPRICE": GASPRICEMetaOpView,
    "EXTCODESIZE": EXTCODESIZEMetaOpView,
    "EXTCODECOPY": EXTCODECOPYMetaOpView,
    "RETURNDATASIZE": RETURNDATASIZEMetaOpView,
    "RETURNDATACOPY": RETURNDATACOPYMetaOpView,
    "EXTCODEHASH": EXTCODEHASHMetaOpView,
    "BLOCKHASH": BLOCKHASHMetaOpView,
    "COINBASE": COINBASEMetaOpView,
    "TIMESTAMP": TIMESTAMPMetaOpView,
    "NUMBER": NUMBERMetaOpView,
    "DIFFICULTY": DIFFICULTYMetaOpView,
    "GASLIMIT": GASLIMITMetaOpView,
    "POP": POPMetaOpView,
    "MLOAD": MLOADMetaOpView,
    "MSTORE": MSTOREMetaOpView,
    "MSTORE8": MSTORE8MetaOpView,
    "SLOAD": SLOADMetaOpView,
    "SSTORE": SSTOREMetaOpView,
    "JUMP": JUMPMetaOpView,
    "JUMPI": JUMPIMetaOpView,
    "PC": PCMetaOpView,
    "MSIZE": MSIZEMetaOpView,
    "GAS": GASMetaOpView,
    "JUMPDEST": JUMPDESTMetaOpView,
    "PUSH": PUSHMetaOpView,
    "DUP": DUPMetaOpView,
    "SWAP": SWAPMetaOpView,
    "CREATE": CREATEMetaOpView,
    "CALL": CALLMetaOpView,
    "CALLCODE": CALLCODEMetaOpView,
    "RETURN": RETURNMetaOpView,
    "DELEGATECALL": DELEGATECALLMetaOpView,
    "CREATE2": CREATE2MetaOpView,
    "STATICCALL": STATICCALLMetaOpView,
    "REVERT": REVERTMetaOpView,
    "SELFDESTRUCT": SELFDESTRUCTMetaOpView,
    "CONST": CONSTMetaOpView,
    "LOG": LOGMetaOpView,
}
