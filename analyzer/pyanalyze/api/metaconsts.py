import operator
from enum import Enum

class OpAction(Enum):
    IS_DESCENDANT = "is_descendant"
    IS_NOT_DESCENDANT = "is_not_descendant"
    IS_ANCESTOR = "is_ancestor"
    IS_NOT_ANCESTOR = "is_not_ancestor"
    IS_CHILD = "is_child"
    IS_PARENT = "is_parent"
    IS_VALUE_LT = "is_value_lt"
    IS_VALUE_GT = "is_value_gt"
    IS_VALUE_EQ = "is_value_eq"
    IS_VALUE_NE = "is_value_ne"
    IS_VALUE_LE = "is_value_le"
    IS_VALUE_GE = "is_value_ge"
    IS_ADDRESS_EQ = "is_address_eq"
    IS_ADDRESS_NE = "is_address_ne"

operator_map = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}

OP_INDEX = 0
CALL_INDEX = 1
PC = 2
DEPTH = 3
