from pyanalyze.vandal.tac_cfg import TACGraph, TACAssignOp
import pyanalyze.vandal.opcodes as opcodes
from pyanalyze.api.metaop import MetaOp, op_name_to_metaop, metaop_to_op_name
from pyanalyze.api.metaopview import *
from pyanalyze.api.metavariable import MetaVariable


class MetaOpLoader:
    def __init__(self, cfg: TACGraph, possible_ops : list[MetaOp]):
        self.ops: dict[str, MetaOpView] = {}

        self._load(cfg, possible_ops)

    def get_ops(self, op_name: str, **kwargs) -> MetaOpView:
        if op_name not in self.ops:
            return None

        return self.ops[op_name].filter(**kwargs)

    def _load(self, cfg: TACGraph, possible_ops : list[MetaOp]):
        vars = {}
        ops = {}
        addresses: dict[int, str] = {1: cfg.sc_addr.lower()}

        supported_ops = []
        for op_cls in possible_ops:
            supported_ops.append(metaop_to_op_name[op_cls])

        for block in cfg.blocks:
            for op in block.tac_ops:
                used_var_names = []
                def_var_name = None
                value = None
                meta_op = None

                if op.opcode.name not in self.ops:
                    self.ops[op.opcode.name] = []

                if op.opcode != opcodes.CONST:
                    used_var_names = [var.value.name for var in op.args]

                if op.opcode.is_call():
                    addresses[op.depth + 1] = hex(
                        next(iter(op.args[1].value.value))
                    ).lower()

                if isinstance(op, TACAssignOp):
                    def_var_name = op.lhs.name

                    if op.lhs.is_finite:
                        value = op.lhs.values.const_value

                meta_op_type = op_name_to_metaop[op.opcode.name]

                if op.opcode.name not in supported_ops:
                    if def_var_name is not None:
                        used_vars = [vars[used_var] for used_var in used_var_names]
                        def_var = MetaVariable(def_var_name, value, used_vars)
                        vars[def_var_name] = def_var

                        for used_var in used_vars:
                            used_var._children.append(def_var)
            
                    continue

                if def_var_name is not None:
                    used_vars = [vars[used_var] for used_var in used_var_names]
                    def_var = MetaVariable(def_var_name, value, used_vars)
                    vars[def_var_name] = def_var

                    for used_var in used_vars:
                        used_var._children.append(def_var)

                    meta_op = meta_op_type(
                        op.op_index,
                        op.call_index,
                        op.pc,
                        op.opcode.name,
                        op.depth,
                        used_vars,
                        def_var,
                    )
                else:
                    used_vars = [vars[used_var] for used_var in used_var_names]
                    meta_op = meta_op_type(
                        op.op_index,
                        op.call_index,
                        op.pc,
                        op.opcode.name,
                        op.depth,
                        used_vars,
                    )

                if op.opcode.name not in ops:
                    ops[op.opcode.name] = []
                ops[op.opcode.name].append(meta_op)

                meta_op._op_ws_index = len(ops[op.opcode.name]) - 1

        for op_name, meta_ops in ops.items():
            self.ops[op_name] = op_name_to_opview[op_name](op_name, meta_ops, addresses)
