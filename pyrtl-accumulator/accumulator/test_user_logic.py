from pyrtl import Input, Output, Simulation, temp_working_block

from .user_logic import AccumulatorLogic
from .states import SessionStates

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

        sim = Simulation()

        def v(x):
            return x.value

        S = SessionStates
        sim.step_multiple(
            provided_inputs={
                'new_state': [1, 1, 1, 1, 1],
                'fsm_state': [v(S.CHOICE), v(S.ADDU), v(S.ADDI),
                                          v(S.RESULT), v(S.CHOICE)],
                'recv_data': [0, 5, -2, 1, 0]

            },
            expected_outputs={
                'accumulator_send_data': [0, 0, 0, 3, 0]
            }
        )
