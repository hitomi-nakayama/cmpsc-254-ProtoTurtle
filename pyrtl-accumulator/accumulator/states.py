from enum import auto, Enum
from dataclasses import dataclass

import pyrtl
from pyrtl import conditional_assignment, WireVector

from .fsm import FSM

class OneHotEnum(Enum):
    """An Enum which counts upward using one-hot values."""
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return 2 ** count


class SessionTransitions(Enum):
    WAIT = 0  # added to make the fsm asynchronous
    U8 = auto()
    U8_TO_LOOP = auto()
    I16 = auto()
    I16_TO_LOOP = auto()
    GET_RESULT = auto()
    END = auto()
    RESET = auto()


SESSION_TRANSITION_BITWIDTH = 4

class SessionStates(Enum):
    CHOICE = 0
    ADDU = auto()
    ADDI = auto()
    RESULT = auto()

SESSION_STATE_NAMES = [x.name for x in SessionStates]


SESSION_STATE_BITWIDTH = 2

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
        f'CHOICE + {v(T.U8)} -> ADDU, {new_val("ADDU")}',
        f'CHOICE + {v(T.I16)} -> ADDI, {new_val("ADDI")}',
        f'CHOICE + {v(T.GET_RESULT)} -> RESULT, {new_val("RESULT")}',
        f'ADDU + {v(T.U8_TO_LOOP)} -> CHOICE, {new_val("CHOICE")}',
        f'ADDI + {v(T.I16_TO_LOOP)} -> CHOICE, {new_val("CHOICE")}',
        f'RESULT + {v(T.END)} -> CHOICE, {new_val("CHOICE")}',

        # We add the wait transitions because we want our circuit design to be
        # async.
        f'CHOICE + {v(T.WAIT)} -> CHOICE, {old_val("CHOICE")}',
        f'ADDU + {v(T.WAIT)} -> ADDU, {old_val("ADDU")}',
        f'ADDI + {v(T.WAIT)} -> ADDI, {old_val("ADDI")}',
        f'RESULT + {v(T.WAIT)} -> RESULT, {old_val("RESULT")}',

        # this is a hack so that we get the "new state" bit upon resetting.
        f'all + {v(T.RESET)} -> CHOICE, {new_val("CHOICE")}'
    ]

    return FSM(states=SESSION_STATE_NAMES,
               input_bitwidth=SESSION_TRANSITION_BITWIDTH,
               output_bitwidth=output_bitwidth + 1, rulesList=rules)


def main():
    input_wire = pyrtl.Input(bitwidth=SESSION_TRANSITION_BITWIDTH, name="input")
    state = pyrtl.Output(bitwidth=SESSION_STATE_BITWIDTH, name="currentState")
    new_state = pyrtl.Output(bitwidth=1, name="newState")

    fsm_output_bitwidth = 3
    output = pyrtl.Output(bitwidth=fsm_output_bitwidth, name="output")

    output_values = {
            'CHOICE': 1,
            'ADDU': 3,
            'ADDI': 4,
            'RESULT': 5
    }

    session_fsm = make_fsm(output_bitwidth=3, output_values=output_values)
    session_fsm <<= input_wire

    output <<= session_fsm()[0][0:-1]
    new_state <<= session_fsm()[0][-1]  # the new_state flag is the msb

    state <<= session_fsm()[1]

    sim_trace = pyrtl.SimulationTrace()
    sim = pyrtl.Simulation(tracer=sim_trace)
    T = SessionTransitions

    input_inputs = [T.RESET, T.WAIT, T.WAIT, T.U8, T.WAIT, T.U8_TO_LOOP, T.GET_RESULT, T.WAIT, T.END, T.WAIT, T.WAIT]
    sim_inputs = {
        'input' : [x.value for x in input_inputs]
    }
    sim.step_multiple(sim_inputs)
    sim_trace.render_trace(trace_list=['input', 'currentState', 'output', 'newState'])


if __name__ == '__main__':
    main()
