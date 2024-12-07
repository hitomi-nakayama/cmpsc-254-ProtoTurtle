"""This is the logic that the user would normally implement themselves"""

from pyrtl import conditional_assignment, Input, Output, Register, WireVector

from .states import NEW_STATE_BITWIDTH, SessionStates, SessionTransitions, SESSION_STATE_BITWIDTH


ACCUMULATOR_REG_BITWIDTH = 16
ACCUMULATOR_IN_DATA_BITWIDTH = 16
ACCUMULATOR_OUT_DATA_BITWIDTH = 16

CLIENT_IN_DATA_BITWIDTH = ACCUMULATOR_OUT_DATA_BITWIDTH
CLIENT_OUT_DATA_BITWIDTH = ACCUMULATOR_IN_DATA_BITWIDTH

class AccumulatorLogic:
    def __init__(self, name=''):
        self.fsm_state = WireVector(bitwidth=SESSION_STATE_BITWIDTH,
                                    name=concat_name('accumulator_fsm_state', name))
        self.new_state = WireVector(bitwidth=NEW_STATE_BITWIDTH,
                                    name=concat_name('accumulator_new_state', name))
        self.send_data = WireVector(bitwidth=ACCUMULATOR_OUT_DATA_BITWIDTH,
                                    name=concat_name('accumulator_send_data', name))
        self.recv_data = WireVector(bitwidth=ACCUMULATOR_IN_DATA_BITWIDTH,
                                    name=concat_name('accumulator_recv_data', name))
        self.accumulator = Register(ACCUMULATOR_REG_BITWIDTH,
                                    name=concat_name('accumulator_reg', name),
                                    reset_value=0)

        # on session
        with conditional_assignment:
            with self.fsm_state == SessionStates.CHOICE.value:
                pass
            with self.fsm_state == SessionStates.ADDU.value:
                self.accumulator.next |= self.accumulator + self.recv_data[:8]
            with self.fsm_state == SessionStates.ADDI.value:
                self.accumulator.next |= self.accumulator + self.recv_data
            with self.fsm_state == SessionStates.RESULT.value:
                self.send_data |= self.accumulator
                self.accumulator.next |= 0



def concat_name(base_name: str, suffix: str | None = None):
    if suffix:
        return base_name + '_' + suffix
    return base_name


def main():
    from pyrtl import Simulation


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


if __name__ == '__main__':
    main()
