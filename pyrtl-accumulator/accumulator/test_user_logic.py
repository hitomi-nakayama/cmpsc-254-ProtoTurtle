from pyrtl import Input, Output, Simulation, temp_working_block

from .user_logic import AccumulatorLogic, ClientLogic
from .states import LOOP_SEQ_BITWIDTH, SessionChoices, SessionStates
from .reports import check_step_multiple

def test_accumulator():
    with temp_working_block():
        acc_logic = AccumulatorLogic()

        fsm_state = Input(bitwidth=len(acc_logic.fsm_state), name='fsm_state')
        acc_logic.fsm_state <<= fsm_state

        new_state = Input(bitwidth=len(acc_logic.new_state), name='new_state')
        acc_logic.new_state <<= new_state

        recv_data = Input(bitwidth=len(acc_logic.recv_data), name='recv_data')
        acc_logic.recv_data <<= recv_data

        send_data = Output(name='send_data')
        send_data <<= acc_logic.send_data

        send = Output(name='send')
        send <<= acc_logic.send

        received = Output(name='received')
        received <<= acc_logic.received

        S = SessionStates
        check_step_multiple(
            provided_inputs={
                'new_state': [1, 1, 1, 1, 1],
                'fsm_state': [S.CHOICE, S.ADDU, S.ADDI, S.RESULT, S.CHOICE],
                'recv_data': [0, 5, -2, 1, 0]

            },
            expected_outputs={
                'send_data': [0, 0, 0, 3, 0],
                'send':      [0, 0, 0, 1, 0],
                'received':  [0, 1, 1, 0, 0]
            }
        )

def test_client():
    with temp_working_block():
        logic = ClientLogic()

        fsm_state = Input(bitwidth=len(logic.fsm_state), name='fsm_state')
        logic.fsm_state <<= fsm_state

        new_state = Input(bitwidth=len(logic.new_state), name='new_state')
        logic.new_state <<= new_state

        recv_data = Input(bitwidth=len(logic.recv_data), name='recv_data')
        logic.recv_data <<= recv_data

        loop_seq = Input(bitwidth=LOOP_SEQ_BITWIDTH, name='loop_seq')
        logic.loop_seq <<= loop_seq

        send_data = Output(name='send_data')
        send_data <<= logic.send_data

        send = Output(name='send')
        send <<= logic.send

        received = Output(name='received')
        received <<= logic.received

        choice = Output(name='choice')
        choice <<= logic.choice

        debug_output = Output(name='debug_output')
        debug_output <<= logic.debug_output

        C = SessionChoices
        S = SessionStates
        check_step_multiple(
            provided_inputs={
                'new_state': [1, 1, 1, 1, 1, 1, 1],
                'fsm_state': [S.CHOICE, S.ADDU, S.CHOICE, S.ADDI, S.CHOICE,
                              S.RESULT, S.CHOICE],
                'loop_seq': [0, 1, 1, 2, 2, 3, 3],
                'recv_data': [0, 0, 0, 0, 0, 12, 0]
            },
            expected_outputs={
                'send_data':    [0, 15, 0, 2**16 - 3, 0, 0, 0],
                'send':         [0, 1, 0, 1, 0, 0, 0],
                'received':     [0, 0, 0, 0, 0, 1, 0],
                'debug_output': [0, 0, 0, 0, 0, 12, 0]
            }
        )
