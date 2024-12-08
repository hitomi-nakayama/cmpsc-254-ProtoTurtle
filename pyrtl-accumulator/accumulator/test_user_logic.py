from pyrtl import Input, Output, Simulation, temp_working_block

from .user_logic import AccumulatorLogic
from .states import SessionStates
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
