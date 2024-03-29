from pyanalyze.api.metaconsts import *

class OpFilter:
    def __init__(self, operator: str, attribute: str = None, value: int = None):
        if operator not in operator_map and not callable(operator):
            raise ValueError(f"Invalid operator for OpFilter {operator}")

        self.attribute = attribute
        self.operator = operator_map[operator] if operator in operator_map else operator
        self.value = value

class Filters:
    DepthEQ = OpFilter(operator="==", attribute="depth")
    DepthNE = OpFilter(operator="!=", attribute="depth")
    DepthGE = OpFilter(operator=">=", attribute="depth")
    DepthLE = OpFilter(operator="<=", attribute="depth")
    DepthGT = OpFilter(operator=">", attribute="depth")
    DepthLT = OpFilter(operator="<", attribute="depth")
    
    CallIndexEQ = OpFilter(operator="==", attribute="call_index")
    CallIndexNE = OpFilter(operator="!=", attribute="call_index")
    CallIndexGE = OpFilter(operator=">=", attribute="call_index")
    CallIndexLE = OpFilter(operator="<=", attribute="call_index")
    CallIndexGT = OpFilter(operator=">", attribute="call_index")
    CallIndexLT = OpFilter(operator="<", attribute="call_index")

    OpIndexEQ = OpFilter(operator="==", attribute="op_index")
    OpIndexNE = OpFilter(operator="!=", attribute="op_index")
    OpIndexGE = OpFilter(operator=">=", attribute="op_index")
    OpIndexLE = OpFilter(operator="<=", attribute="op_index")
    OpIndexGT = OpFilter(operator=">", attribute="op_index")
    OpIndexLT = OpFilter(operator="<", attribute="op_index")
    
    PcIndexEQ = OpFilter(operator="==", attribute="pc")
    PcIndexNE = OpFilter(operator="!=", attribute="pc")
    PcIndexGE = OpFilter(operator=">=", attribute="pc")
    PcIndexLE = OpFilter(operator="<=", attribute="pc")
    PcIndexGT = OpFilter(operator=">", attribute="pc")
    PcIndexLT = OpFilter(operator="<", attribute="pc")

class DiscreteFilters:
    @staticmethod
    def depth_eq(value):
        return OpFilter(operator="==", attribute="depth", value=value)
    
    @staticmethod
    def depth_ne(value):
        return OpFilter(operator="!=", attribute="depth", value=value)
    
    @staticmethod
    def depth_gt(value):
        return OpFilter(operator=">", attribute="depth", value=value)
    
    @staticmethod
    def depth_lt(value):
        return OpFilter(operator="<", attribute="depth", value=value)
    
    @staticmethod
    def depth_ge(value):
        return OpFilter(operator=">=", attribute="depth", value=value)
    
    @staticmethod
    def depth_le(value):
        return OpFilter(operator="<=", attribute="depth", value=value)
    
    @staticmethod
    def call_index_eq(value):
        return OpFilter(operator="==", attribute="call_index", value=value)
    
    @staticmethod
    def call_index_ne(value):
        return OpFilter(operator="!=", attribute="call_index", value=value)
    
    @staticmethod
    def call_index_gt(value):
        return OpFilter(operator=">", attribute="call_index", value=value)
    
    @staticmethod
    def call_index_lt(value):
        return OpFilter(operator="<", attribute="call_index", value=value)
    
    @staticmethod
    def call_index_ge(value):
        return OpFilter(operator=">=", attribute="call_index", value=value)
    
    @staticmethod
    def call_index_le(value):
        return OpFilter(operator="<=", attribute="call_index", value=value)
    
    @staticmethod
    def op_index_eq(value):
        return OpFilter(operator="==", attribute="op_index", value=value)
    
    @staticmethod
    def op_index_ne(value):
        return OpFilter(operator="!=", attribute="op_index", value=value)
    
    @staticmethod
    def op_index_gt(value):
        return OpFilter(operator=">", attribute="op_index", value=value)
    
    @staticmethod
    def op_index_lt(value):
        return OpFilter(operator="<", attribute="op_index", value=value)
    
    @staticmethod
    def op_index_ge(value):
        return OpFilter(operator=">=", attribute="op_index", value=value)
    
    @staticmethod
    def op_index_le(value):
        return OpFilter(operator="<=", attribute="op_index", value=value)
    
    @staticmethod
    def pc_eq(value):
        return OpFilter(operator="==", attribute="pc", value=value)
    
    @staticmethod
    def pc_ne(value):
        return OpFilter(operator="!=", attribute="pc", value=value)
    
    @staticmethod
    def pc_gt(value):
        return OpFilter(operator=">", attribute="pc", value=value)
    
    @staticmethod
    def pc_lt(value):
        return OpFilter(operator="<", attribute="pc", value=value)
    
    @staticmethod
    def pc_ge(value):
        return OpFilter(operator=">=", attribute="pc", value=value)
    
    @staticmethod
    def pc_le(value):
        return OpFilter(operator="<=", attribute="pc", value=value)
    
    @staticmethod
    def address_eq(value):
        return OpFilter(operator="==", attribute="address", value=value)
    
    @staticmethod
    def address_ne(value):
        return OpFilter(operator="!=", attribute="address", value=value)
    
    @staticmethod
    def address_gt(value):
        return OpFilter(operator=">", attribute="address", value=value)
    
    @staticmethod
    def address_lt(value):
        return OpFilter(operator="<", attribute="address", value=value)
    
    @staticmethod
    def address_ge(value):
        return OpFilter(operator=">=", attribute="address", value=value)
    
    @staticmethod
    def address_le(value):
        return OpFilter(operator="<=", attribute="address", value=value)