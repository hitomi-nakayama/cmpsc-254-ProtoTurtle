from enum import auto, Enum
from dataclasses import dataclass

import pyrtl
from pyrtl import conditional_assignment, WireVector

from .fsm import FSM
from .bit_enum import BitEnum


class SessionTransitions(BitEnum):
    WAIT = auto()  # added to make the fsm asynchronous
    U8 = auto()
    U8_TO_LOOP = auto()
    I16 = auto()
    I16_TO_LOOP = auto()
    GET_RESULT = auto()
    END = auto()
    RESET = auto()


class SessionStates(BitEnum):
    CHOICE = auto()
    ADDU = auto()
    ADDI = auto()
    RESULT = auto()

SESSION_STATE_NAMES = [x.name for x in SessionStates]


NEW_STATE_BITWIDTH = 1

def make_fsm(output_bitwidth: int, output_values: dict[str, int]):
    """The highest bit of the output is high when it is a new state.
    output_bitwidth is the size of the state values (excluding the new state bit)"""
    def v(enumeration):
        return enumeration.value

    def old_val(state: str) -> int:
        return output_values[state]

    def new_val(state: str) -> int:
        return output_values[state] + 2 ** output_bitwidth

    T = SessionTransitions
    rules = [
        # the states don't have underscores or numbers due to a limitation of
        # fsm.py that we don't have time to fix right now.
        f'CHOICE + {T.U8} -> ADDU, {new_val("ADDU")}',
        f'CHOICE + {T.I16} -> ADDI, {new_val("ADDI")}',
        f'CHOICE + {T.GET_RESULT} -> RESULT, {new_val("RESULT")}',
        f'ADDU + {T.U8_TO_LOOP} -> CHOICE, {new_val("CHOICE")}',
        f'ADDI + {T.I16_TO_LOOP} -> CHOICE, {new_val("CHOICE")}',
        f'RESULT + {T.END} -> CHOICE, {new_val("CHOICE")}',

        # We add the wait transitions because we want our circuit design to be
        # async.
        f'CHOICE + {T.WAIT} -> CHOICE, {old_val("CHOICE")}',
        f'ADDU + {T.WAIT} -> ADDU, {old_val("ADDU")}',
        f'ADDI + {T.WAIT} -> ADDI, {old_val("ADDI")}',
        f'RESULT + {T.WAIT} -> RESULT, {old_val("RESULT")}',

        # this is a hack so that we get the "new state" bit upon resetting.
        f'all + {T.RESET} -> CHOICE, {new_val("CHOICE")}'
    ]

    return FSM(states=SESSION_STATE_NAMES,
               input_bitwidth=SessionTransitions.bitwidth(),
               output_bitwidth=output_bitwidth + 1, rulesList=rules)
