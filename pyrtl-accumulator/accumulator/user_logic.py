"""This is the logic that the user would normally implement themselves"""

from pyrtl import conditional_assignment, Input, Output, Register, WireVector

from .states import (LOOP_SEQ_BITWIDTH, NEW_STATE_BITWIDTH, SessionChoices,
                     SessionStates, SessionTransitions)

ACCUMULATOR_REG_BITWIDTH = 16
ACCUMULATOR_IN_DATA_BITWIDTH = 16
ACCUMULATOR_OUT_DATA_BITWIDTH = 16

CLIENT_IN_DATA_BITWIDTH = ACCUMULATOR_OUT_DATA_BITWIDTH
CLIENT_OUT_DATA_BITWIDTH = ACCUMULATOR_IN_DATA_BITWIDTH

class AccumulatorLogic:
    def __init__(self):
        self.fsm_state = WireVector(bitwidth=SessionStates.bitwidth())
        self.new_state = WireVector(bitwidth=NEW_STATE_BITWIDTH)
        self.send_data = WireVector(bitwidth=ACCUMULATOR_OUT_DATA_BITWIDTH)
        self.recv_data = WireVector(bitwidth=ACCUMULATOR_IN_DATA_BITWIDTH)
        self.accumulator = Register(ACCUMULATOR_REG_BITWIDTH)

        # user logic sets this high when a value has been read
        self.received = WireVector(bitwidth=1)

        # user logic sets this high when a value is sent
        self.send = WireVector(bitwidth=1)

        self._connect_logic()


    def _connect_logic(self):
        # on session
        with conditional_assignment:
            with self.fsm_state == SessionStates.CHOICE.value:
                # the user doesn't perform any logic here.
                # We are waiting for the client to tell us what to do next
                pass
            with self.fsm_state == SessionStates.ADDU.value:
                self.accumulator.next |= self.accumulator + self.recv_data[:8]
                self.received |= 1
            with self.fsm_state == SessionStates.ADDI.value:
                self.accumulator.next |= self.accumulator + self.recv_data
                self.received |= 1
            with self.fsm_state == SessionStates.RESULT.value:
                self.send_data |= self.accumulator
                self.accumulator.next |= 0
                self.send |= 1


class ClientLogic:
    def __init__(self):
        self.fsm_state = WireVector(bitwidth=SessionStates.bitwidth())
        self.new_state = WireVector(bitwidth=NEW_STATE_BITWIDTH)

        # tells us which iteration of the loop we're in
        self.loop_seq = WireVector(bitwidth=LOOP_SEQ_BITWIDTH)

        # which choice to take?
        self.choice = WireVector(bitwidth=SessionChoices.bitwidth())

        self.send_data = WireVector(bitwidth=ACCUMULATOR_IN_DATA_BITWIDTH)
        self.recv_data = WireVector(bitwidth=ACCUMULATOR_OUT_DATA_BITWIDTH)

        self.debug_output = WireVector(bitwidth=ACCUMULATOR_OUT_DATA_BITWIDTH)

        # user logic sets this high when a value has been read
        self.received = WireVector(bitwidth=1)

        # user logic sets this high when a value is sent
        self.send = WireVector(bitwidth=1)

        self._connect_logic()


    def _connect_logic(self):
        C = SessionChoices
        # on session
        with conditional_assignment:
            with self.fsm_state == SessionStates.CHOICE.value:
                with self.loop_seq == 0:
                    self.choice |= C.ADDEND_U8
                with self.loop_seq == 1:
                    self.choice |= C.ADDEND_I16
                with self.loop_seq == 2:
                    self.choice |= C.RESULT_I16

            with self.fsm_state == SessionStates.ADDU.value:
                self.send_data |= 15
                self.send |= 1
            with self.fsm_state == SessionStates.ADDI.value:
                self.send_data |= -3
                self.send |= 1
            with self.fsm_state == SessionStates.RESULT.value:
                self.debug_output |= self.recv_data
                self.received |= 1
