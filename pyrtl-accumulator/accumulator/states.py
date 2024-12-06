from enum import auto, Enum

import pyrtl

from .fsm import FSM

class OneHotEnum(Enum):
    """An Enum which counts upward using one-hot values."""
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return 2 ** count


class SessionTransitions(Enum):
    WAIT = auto()  # added because original is syncronous (I think??)
    LOOP_YES = auto()
    U8 = auto()
    U8_TO_LOOP = auto()
    I16 = auto()
    I16_TO_LOOP = auto()
    LOOP_NO = auto()
    END = auto()


SESSION_TRANSITIONS_BITWIDTH = 3


SESSION_STATES = ['LOOPCHOICE', 'DTYPECHOICE', 'ADDU', 'ADDI',
                  'RESULT']

def make_session_transition_table():
    def v(enumeration):
        return enumeration.value

    T = SessionTransitions
    rules = [
        f'LOOPCHOICE + {v(T.LOOP_YES)} -> DTYPECHOICE, 1',
        f'LOOPCHOICE + {v(T.LOOP_NO)} -> RESULT, 1',
        f'DTYPECHOICE + {v(T.U8)} -> ADDU, 2',
        f'DTYPECHOICE + {v(T.I16)} -> ADDI, 3',
        f'ADDU + {v(T.U8_TO_LOOP)} -> LOOPCHOICE, 0',
        f'ADDI + {v(T.I16_TO_LOOP)} -> LOOPCHOICE, 0',
        f'RESULT + {v(T.END)} -> LOOPCHOICE, 0'
    ]

    return FSM(states=SESSION_STATES,
               input_bitwidth=SESSION_TRANSITIONS_BITWIDTH,
               output_bitwidth=1, rulesList=rules)




input_wire = pyrtl.Input(bitwidth=2, name="input")
state = pyrtl.Output(bitwidth=2, name="currentState")
output = pyrtl.Output(bitwidth=1, name="output")

session_fsm = make_session_transition_table()
session_fsm <<= input_wire

output <<= session_fsm()[0]
state <<= session_fsm()[1]

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)
T = SessionTransitions
sim_inputs = {
    'input' : f'{T.LOOP_YES.value}{T.LOOP_YES.value}{T.U8.value}{T.LOOP_YES.value}{T.LOOP_YES.value}'
}
sim.step_multiple(sim_inputs)
sim_trace.render_trace(trace_list=['input', 'currentState', 'output'])
