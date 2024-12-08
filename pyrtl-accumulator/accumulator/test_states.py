from pyrtl import Input, Output, Simulation, SimulationTrace, temp_working_block

from .states import SessionFSM, SessionStates, SessionTransitions
from .reports import check_step_multiple

def test_fsm():
    with temp_working_block():
        output_values = {
                'CHOICE': 1,
                'ADDU': 3,
                'ADDI': 4,
                'RESULT': 5
        }

        fsm = SessionFSM(output_values)

        fsm_input = Input(bitwidth=SessionTransitions.bitwidth(), name="input")
        fsm <<= fsm_input

        state = Output(name="state")
        state <<= fsm.state

        new_state = Output(name="new_state")
        new_state <<= fsm.new_state

        output = Output(name="output")
        output <<= fsm.output

        S = SessionStates
        T = SessionTransitions
        check_step_multiple(
            provided_inputs={
                'input' : [T.RESET, T.WAIT, T.WAIT, T.U8, T.WAIT, T.NEXT,
                          T.GET_RESULT, T.WAIT, T.NEXT, T.WAIT, T.WAIT]
            },
            expected_outputs={
                'new_state': [0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
                'state': [S.CHOICE, S.CHOICE, S.CHOICE, S.CHOICE, S.ADDU, S.ADDU,
                          S.CHOICE, S.RESULT, S.RESULT, S.CHOICE, S.CHOICE],
                'output': [0, 1, 1, 1, 3, 3, 1, 5, 5, 1, 1]
            },
        )
