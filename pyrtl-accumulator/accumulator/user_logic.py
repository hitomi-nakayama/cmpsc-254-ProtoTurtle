"""This is the logic that the user would normally implement themselves"""

from pyrtl import conditional_assignment, Input, Output, Register, WireVector

from .states import NEW_STATE_BITWIDTH, SessionStates, SessionTransitions

ACCUMULATOR_REG_BITWIDTH = 16
ACCUMULATOR_IN_DATA_BITWIDTH = 16
ACCUMULATOR_OUT_DATA_BITWIDTH = 16

CLIENT_IN_DATA_BITWIDTH = ACCUMULATOR_OUT_DATA_BITWIDTH
CLIENT_OUT_DATA_BITWIDTH = ACCUMULATOR_IN_DATA_BITWIDTH

class AccumulatorLogic:
    def __init__(self, name=''):
        self.fsm_state = WireVector(bitwidth=SessionStates.bitwidth(),
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
    pass


if __name__ == '__main__':
    main()
