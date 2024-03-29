from pyanalyze.api.metavariable import MetaVariable


class MetaOp:
    def __init__(
        self, op_index: int, call_index: int, pc: int, opcode: str, depth: int, *args
    ):
        self.op_index = op_index
        self.call_index = call_index
        self.pc = pc
        self.opcode = opcode
        self.depth = depth
        self.address = None
        self._op_ws_index = None

    def to_np(self):
        return [self.op_index, self.call_index, self.pc, self.depth]

    @staticmethod
    def base_attributes():
        return ["op_index", "call_index", "pc", "depth", 'opcode', 'address', '_op_ws_index']

    def __repr__(self) -> str:
        return f"MetaOp: op:{self.op_index}, call:{self.call_index}, pc:{self.pc}, depth:{self.depth}, code:{self.opcode}"

    def get_vars(self):
        base = list(MetaOp.__dict__.keys()) + MetaOp.base_attributes()

        return {key: getattr(self, key).to_dict() for key in self.__dict__.keys() if key not in base}

    def to_dict(self):
        vars = self.get_vars()
        if vars:
            return {
                "op_index": self.op_index,
                "call_index": self.call_index,
                "pc": self.pc,
                "opcode": self.opcode,
                "depth": self.depth,
                "address": self.address,
                "vars": vars,
            } 
        return {
            "op_index": self.op_index,
            "call_index": self.call_index,
            "pc": self.pc,
            "opcode": self.opcode,
            "depth": self.depth,
            "address": self.address,
        }

class UnaryOp(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        result: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.operand = used_vars[0]
        self.result = result


class BinaryOp(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        result: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.left = used_vars[0]
        self.right = used_vars[1]
        self.result = result


class TernaryOp(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        result: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.first = used_vars[0]
        self.second = used_vars[1]
        self.third = used_vars[2]
        self.result = result


class CONST(MetaOp): ...


class STOP(MetaOp): ...


class ADD(BinaryOp): ...


class MUL(BinaryOp): ...


class SUB(BinaryOp): ...


class DIV(BinaryOp): ...


class SDIV(BinaryOp): ...


class MOD(BinaryOp): ...


class SMOD(BinaryOp): ...


class ADDMOD(TernaryOp): ...


class MULMOD(TernaryOp): ...


class EXP(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        result: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.base = used_vars[0]
        self.exp = used_vars[1]
        self.result = result


class SIGNEXTEND(BinaryOp): ...


class LT(BinaryOp): ...


class GT(BinaryOp): ...


class SLT(BinaryOp): ...


class SGT(BinaryOp): ...


class EQ(BinaryOp): ...


class ISZERO(UnaryOp): ...


class AND(BinaryOp): ...


class OR(BinaryOp): ...


class XOR(BinaryOp): ...


class NOT(UnaryOp): ...


class BYTE(BinaryOp): ...


class SHL(BinaryOp): ...


class SHR(BinaryOp): ...


class SHA3(BinaryOp): ...


class ADDRESS(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        address: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.address = address


class BALANCE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        balance: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.address = used_vars[0]
        self.balance = balance


class ORIGIN(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        address: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.address = address


class CALLER(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        address: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.address = address


class CALLVALUE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        value: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.value = value


class CALLDATALOAD(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        value: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.index = used_vars[0]
        self.value = value


class CALLDATASIZE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        size: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.size = size


class CALLDATACOPY(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.mem_offset = used_vars[0]
        self.data_offset = used_vars[1]
        self.size = used_vars[2]


class CODESIZE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        size: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.size = size


class CODECOPY(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.mem_offset = used_vars[0]
        self.code_offset = used_vars[1]
        self.size = used_vars[2]


class GASPRICE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        price: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.price = price


class EXTCODESIZE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        size: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.address = used_vars[0]
        self.size = size


class EXTCODECOPY(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.address = used_vars[0]
        self.mem_offset = used_vars[1]
        self.code_offset = used_vars[2]
        self.size = used_vars[3]


class RETURNDATASIZE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        size: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.size = size


class RETURNDATACOPY(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.mem_offset = used_vars[0]
        self.data_offset = used_vars[1]
        self.size = used_vars[2]


class EXTCODEHASH(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        code_hash: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.address = used_vars[0]
        self.code_hash = code_hash


class BLOCKHASH(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        block_hash: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.block_number = used_vars[0]
        self.block_hash = block_hash


class COINBASE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        address: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.address = address


class TIMESTAMP(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        timestamp: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.timestamp = timestamp


class NUMBER(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        block_number: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.block_number = block_number


class DIFFICULTY(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        difficulty: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.difficulty = difficulty


class GASLIMIT(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        gas_limit: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.gas_limit = gas_limit


class POP(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.value = used_vars[0]


class MLOAD(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        value: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.mem_offset = used_vars[0]
        self.value = value


class MSTORE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.mem_offset = used_vars[0]
        self.value = used_vars[1]


class MSTORE8(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.mem_offset = used_vars[0]
        self.value = used_vars[1]


class SLOAD(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        value: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.key = used_vars[0]
        self.value = value


class SSTORE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.key = used_vars[0]
        self.value = used_vars[1]


class JUMP(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.destination = used_vars[0]


class JUMPI(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.condition = used_vars[0]
        self.destination = used_vars[1]


class PC(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        pc_value: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.pc_value = pc_value


class MSIZE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        size: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.size = size


class GAS(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        gas: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.gas_remaining = gas


class JUMPDEST(MetaOp):
    def __init__(
        self, op_index: int, call_index: int, pc: int, opcode: str, depth: int, *args
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)


class PUSH(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        value: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.value = value


class DUP(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        value: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.value = value


class SWAP(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        value: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.value = value


# Not covering log right now, not used by vandal


class CREATE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        address: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.value = used_vars[0]
        self.mem_offset = used_vars[1]
        self.size = used_vars[2]
        self.address = address


class CALL(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        success: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.gas = used_vars[0]
        self.address = used_vars[1]
        self.value = used_vars[2]
        self.in_offset = used_vars[3]
        self.in_size = used_vars[4]
        self.out_offset = used_vars[5]
        self.out_size = used_vars[6]
        self.success = success


class CALLCODE(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        success: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.gas = used_vars[0]
        self.address = used_vars[1]
        self.value = used_vars[2]
        self.in_offset = used_vars[3]
        self.in_size = used_vars[4]
        self.out_offset = used_vars[5]
        self.out_size = used_vars[6]
        self.success = success


class RETURN(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.mem_offset = used_vars[0]
        self.size = used_vars[1]


class DELEGATECALL(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        success: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.gas = used_vars[0]
        self.address = used_vars[1]
        self.in_offset = used_vars[2]
        self.in_size = used_vars[3]
        self.out_offset = used_vars[4]
        self.out_size = used_vars[5]
        self.success = success


class CREATE2(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        address: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.value = used_vars[0]
        self.mem_offset = used_vars[1]
        self.size = used_vars[2]
        self.salt = used_vars[3]
        self.address = address


class STATICCALL(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        success: MetaVariable,
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.gas = used_vars[0]
        self.address = used_vars[1]
        self.in_offset = used_vars[2]
        self.in_size = used_vars[3]
        self.out_offset = used_vars[4]
        self.out_size = used_vars[5]
        self.success = success


class REVERT(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.mem_offset = used_vars[0]
        self.size = used_vars[1]


class SELFDESTRUCT(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.address = used_vars[0]


class LOG(MetaOp):
    def __init__(
        self,
        op_index: int,
        call_index: int,
        pc: int,
        opcode: str,
        depth: int,
        used_vars: list[MetaVariable],
        *args,
    ):
        super().__init__(op_index, call_index, pc, opcode, depth, *args)
        self.offset = used_vars[0]
        self.size = used_vars[1]

        self.topic_0 = None
        self.topic_1 = None
        self.topic_2 = None
        self.topic_3 = None
        self.topic_4 = None

        # there is probably a match with fallthrough that could be used
        if len(used_vars) > 2:
            self.topic_0 = used_vars[2]
        if len(used_vars) > 3:
            self.topic_1 = used_vars[3]
        if len(used_vars) > 4:
            self.topic_2 = used_vars[4]
        if len(used_vars) > 5:
            self.topic_3 = used_vars[5]
        if len(used_vars) > 6:
            self.topic_4 = used_vars[6]
        

op_name_to_metaop = {
    "STOP": STOP,
    "ADD": ADD,
    "MUL": MUL,
    "SUB": SUB,
    "DIV": DIV,
    "SDIV": SDIV,
    "MOD": MOD,
    "SMOD": SMOD,
    "ADDMOD": ADDMOD,
    "MULMOD": MULMOD,
    "EXP": EXP,
    "SIGNEXTEND": SIGNEXTEND,
    "LT": LT,
    "GT": GT,
    "SLT": SLT,
    "SGT": SGT,
    "EQ": EQ,
    "ISZERO": ISZERO,
    "AND": AND,
    "OR": OR,
    "XOR": XOR,
    "NOT": NOT,
    "BYTE": BYTE,
    "SHL": SHL,
    "SHR": SHR,
    "SHA3": SHA3,
    "KECCAK256": SHA3,
    "ADDRESS": ADDRESS,
    "BALANCE": BALANCE,
    "ORIGIN": ORIGIN,
    "CALLER": CALLER,
    "CALLVALUE": CALLVALUE,
    "CALLDATALOAD": CALLDATALOAD,
    "CALLDATASIZE": CALLDATASIZE,
    "CALLDATACOPY": CALLDATACOPY,
    "CODESIZE": CODESIZE,
    "CODECOPY": CODECOPY,
    "GASPRICE": GASPRICE,
    "EXTCODESIZE": EXTCODESIZE,
    "EXTCODECOPY": EXTCODECOPY,
    "RETURNDATASIZE": RETURNDATASIZE,
    "RETURNDATACOPY": RETURNDATACOPY,
    "EXTCODEHASH": EXTCODEHASH,
    "BLOCKHASH": BLOCKHASH,
    "COINBASE": COINBASE,
    "TIMESTAMP": TIMESTAMP,
    "NUMBER": NUMBER,
    "DIFFICULTY": DIFFICULTY,
    "GASLIMIT": GASLIMIT,
    "POP": POP,
    "MLOAD": MLOAD,
    "MSTORE": MSTORE,
    "MSTORE8": MSTORE8,
    "SLOAD": SLOAD,
    "SSTORE": SSTORE,
    "JUMP": JUMP,
    "JUMPI": JUMPI,
    "PC": PC,
    "MSIZE": MSIZE,
    "GAS": GAS,
    "JUMPDEST": JUMPDEST,
    "PUSH": PUSH,
    "DUP": DUP,
    "SWAP": SWAP,
    "CREATE": CREATE,
    "CALL": CALL,
    "CALLCODE": CALLCODE,
    "RETURN": RETURN,
    "DELEGATECALL": DELEGATECALL,
    "CREATE2": CREATE2,
    "STATICCALL": STATICCALL,
    "REVERT": REVERT,
    "SELFDESTRUCT": SELFDESTRUCT,
    "CONST": CONST,
    "LOG": LOG,
}

metaop_to_op_name = {v: k for k, v in op_name_to_metaop.items()}