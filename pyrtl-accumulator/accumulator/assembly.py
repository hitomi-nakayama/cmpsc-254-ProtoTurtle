from pyrtl import WireVector

from .states import AccumulatorFSM, ClientFSM
from .user_logic import (AccumulatorLogic, ACCUMULATOR_OUT_DATA_BITWIDTH,
                         ClientLogic)


class Assembly:
    def __init__(self):
        self.reset = WireVector(bitwidth=1)
        self.debug_output = WireVector(bitwidth=ACCUMULATOR_OUT_DATA_BITWIDTH)
        self.debug_output_valid = WireVector(bitwidth=1)

        self.acc_fsm = AccumulatorFSM()
        self.acc_logic = AccumulatorLogic()
        self.client_fsm = ClientFSM()
        self.client_logic = ClientLogic()

        self._connect()

    def _connect(self):
        self.acc_logic.new_state <<= self.acc_fsm.new_state
        self.acc_logic.fsm_state <<= self.acc_fsm.state
        self.acc_logic.recv_data <<= self.client_logic.send_data

        self.acc_fsm.reset <<= self.reset
        self.acc_fsm.offer <<= self.client_logic.choice
        self.acc_fsm.received <<= self.acc_logic.received
        self.acc_fsm.send <<= self.acc_logic.send

        self.client_logic.new_state <<= self.client_fsm.new_state
        self.client_logic.fsm_state <<= self.client_fsm.state
        self.client_logic.loop_seq <<= self.client_fsm.loop_seq
        self.client_logic.recv_data <<= self.acc_logic.send_data

        self.client_fsm.reset <<= self.reset
        self.client_fsm.choice <<= self.client_logic.choice
        self.client_fsm.received <<= self.client_logic.received
        self.client_fsm.send <<= self.client_logic.send

        self.debug_output <<= self.client_logic.debug_output
        self.debug_output_valid <<= self.client_logic.debug_output_valid
