from enum import auto, Enum
from dataclasses import dataclass

import pyrtl

from .fsm import FSM

class OneHotEnum(Enum):
    """An Enum which counts upward using one-hot values."""
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return 2 ** count


class SessionTransitions(Enum):
    WAIT = 0  # added because original is syncronous (I think??)
    LOOP_YES = auto()
    U8 = auto()
    U8_TO_LOOP = auto()
    I16 = auto()
    I16_TO_LOOP = auto()
    LOOP_NO = auto()
    END = auto()
    RESET = auto()


SESSION_TRANSITIONS_BITWIDTH = 4


SESSION_STATES = ['LOOPCHOICE', 'DTYPECHOICE', 'ADDU', 'ADDI',
                  'RESULT']



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
        f'LOOPCHOICE + {v(T.LOOP_YES)} -> DTYPECHOICE, {new_val("DTYPECHOICE")}',
        f'LOOPCHOICE + {v(T.LOOP_NO)} -> RESULT, {new_val("RESULT")}',
        f'DTYPECHOICE + {v(T.U8)} -> ADDU, {new_val("ADDU")}',
        f'DTYPECHOICE + {v(T.I16)} -> ADDI, {new_val("ADDI")}',
        f'ADDU + {v(T.U8_TO_LOOP)} -> LOOPCHOICE, {new_val("LOOPCHOICE")}',
        f'ADDI + {v(T.I16_TO_LOOP)} -> LOOPCHOICE, {new_val("LOOPCHOICE")}',
        f'RESULT + {v(T.END)} -> LOOPCHOICE, {new_val("LOOPCHOICE")}',

        # We add the wait transitions because we want our circuit design to be
        # async.
        f'LOOPCHOICE + {v(T.WAIT)} -> LOOPCHOICE, {old_val("LOOPCHOICE")}',
        f'DTYPECHOICE + {v(T.WAIT)} -> DTYPECHOICE, {old_val("DTYPECHOICE")}',
        f'ADDU + {v(T.WAIT)} -> ADDU, {old_val("ADDU")}',
        f'ADDI + {v(T.WAIT)} -> ADDI, {old_val("ADDI")}',
        f'RESULT + {v(T.WAIT)} -> LOOPCHOICE, {old_val("RESULT")}',

        # this is a hack so that we get the "new state" bit upon resetting.
        f'all + {v(T.RESET)} -> LOOPCHOICE, {new_val("LOOPCHOICE")}'
    ]

    return FSM(states=SESSION_STATES,
               input_bitwidth=SESSION_TRANSITIONS_BITWIDTH,
               output_bitwidth=output_bitwidth + 1, rulesList=rules)


def main():
    input_wire = pyrtl.Input(bitwidth=SESSION_TRANSITIONS_BITWIDTH, name="input")
    state = pyrtl.Output(bitwidth=3, name="currentState")
    output = pyrtl.Output(bitwidth=4, name="output")
    output_values = {
            'LOOPCHOICE': 1,
            'DTYPECHOICE': 2,
            'ADDU': 3,
            'ADDI': 4,
            'RESULT': 5
    }
    session_fsm = make_fsm(output_bitwidth=3, output_values=output_values)
    session_fsm <<= input_wire

    output <<= session_fsm()[0]
    state <<= session_fsm()[1]

    sim_trace = pyrtl.SimulationTrace()
    sim = pyrtl.Simulation(tracer=sim_trace)
    T = SessionTransitions

    input_inputs = [T.RESET, T.WAIT, T.WAIT, T.LOOP_YES, T.U8, T.WAIT, T.U8_TO_LOOP, T.LOOP_NO, T.END, T.WAIT, T.WAIT]
    sim_inputs = {
        'input' : [x.value for x in input_inputs]
    }
    sim.step_multiple(sim_inputs)
    sim_trace.render_trace(trace_list=['input', 'currentState', 'output'])


if __name__ == '__main__':
    main()
