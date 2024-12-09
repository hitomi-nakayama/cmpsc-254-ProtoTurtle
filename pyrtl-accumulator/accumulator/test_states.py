from pyrtl import Input, Output, Simulation, SimulationTrace, temp_working_block

from .states import (AccumulatorFSM, ClientFSM, SessionChoices, SessionFSM,
                     SessionStates, SessionTransitions)
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


def test_accumulator_fsm():
    with temp_working_block():
        fsm = AccumulatorFSM()

        reset = Input(bitwidth=1, name="reset")
        fsm.reset <<= reset

        offer = Input(bitwidth=SessionChoices.bitwidth(), name='offer')
        fsm.offer <<= offer

        received = Input(bitwidth=1, name='received')
        fsm.received <<= received

        send = Input(bitwidth=1, name='send')
        fsm.send <<= send

        state = Output(name="state")
        state <<= fsm.state

        new_state = Output(name="new_state")
        new_state <<= fsm.new_state


        C = SessionChoices
        S = SessionStates
        T = SessionTransitions
        check_step_multiple(
            provided_inputs={
                'reset': [1, 0, 0, 0, 0, 0, 0, 0, 0],
                'offer': [0, C.NULL, C.ADDEND_I16, C.NULL, C.NULL, C.RESULT_I16,
                          C.NULL, C.NULL, C.NULL],
                'send': [0, 0, 0, 0, 0, 0, 0, 1, 0],
                'received': [0, 0, 0, 0, 1, 0, 0, 0, 0]

            },
            expected_outputs={
                'new_state': [0, 1, 0, 1, 0, 1, 1, 0, 1],
                'state': [0, S.CHOICE, S.CHOICE, S.ADDI, S.ADDI, S.CHOICE,
                          S.RESULT, S.RESULT, S.CHOICE],
            },
        )


def test_client_fsm():
    with temp_working_block():
        fsm = ClientFSM()

        reset = Input(bitwidth=1, name="reset")
        fsm.reset <<= reset

        received = Input(bitwidth=1, name='received')
        fsm.received <<= received

        send = Input(bitwidth=1, name='send')
        fsm.send <<= send

        choice = Input(bitwidth=SessionChoices.bitwidth(), name="choice")
        fsm.choice <<= choice

        state = Output(name="state")
        state <<= fsm.state

        new_state = Output(name="new_state")
        new_state <<= fsm.new_state

        loop_seq = Output(name="loop_seq")
        loop_seq <<= fsm.loop_seq

        C = SessionChoices
        S = SessionStates
        T = SessionTransitions
        check_step_multiple(
            provided_inputs={
                'reset': [1, 0, 0, 0, 0, 0, 0, 0, 0],
                'send': [0, 0, 0, 0, 0, 0, 0, 1, 0],
                'received': [0, 0, 0, 0, 1, 0, 0, 0, 0],
                'choice': [0, C.NULL, C.ADDEND_I16, C.NULL, C.NULL, C.RESULT_I16,
                          C.NULL, C.NULL, C.NULL],
            },
            expected_outputs={
                'new_state': [0, 1, 0, 1, 0, 1, 1, 0, 1],
                'state': [0, S.CHOICE, S.CHOICE, S.ADDI, S.ADDI, S.CHOICE,
                          S.RESULT, S.RESULT, S.CHOICE],

                'loop_seq': [0, 0, 0, 1, 1, 1, 2, 2, 2]
            },
        )
