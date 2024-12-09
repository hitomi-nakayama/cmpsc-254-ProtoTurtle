from collections import defaultdict
from dataclasses import dataclass
from enum import auto, Enum

import pyrtl
from pyrtl import conditional_assignment, otherwise, Register, WireVector

from .fsm import FSM
from .bit_enum import BitEnum
from .wires import bitwidth


class SessionTransitions(BitEnum):
    WAIT = auto()  # added to make the fsm asynchronous
    NEXT = auto()  # go to the next state when there isn't a choice
    U8 = auto()
    I16 = auto()
    GET_RESULT = auto()
    RESET = auto()


class SessionStates(BitEnum):
    CHOICE = auto()
    ADDU = auto()
    ADDI = auto()
    RESULT = auto()

SESSION_STATE_NAMES = [x.name for x in SessionStates]


NEW_STATE_BITWIDTH = 1


class SessionFSM:
    def __init__(self, output_values: dict[str, int] | None = None):
        """The highest bit of the output is high when it is a new state.
        output_bitwidth is the size of the state values (excluding the new state bit)"""

        if output_values:
            output_bitwidth = max(bitwidth(x) for x in output_values.values())
        else:
            output_values = defaultdict(lambda: 0)
            output_bitwidth = 1

        def old_val(state: str) -> int:
            return output_values[state]

        def new_val(state: str) -> int:
            return output_values[state] + 2 ** output_bitwidth

        T = SessionTransitions
        rules = [
            # the states don't have underscores or numbers due to a limitation of
            # fsm.py that we don't have time to fix right now.
            f'CHOICE + {T.U8} -> ADDU, {new_val("ADDU")}',
            f'CHOICE + {T.I16} -> ADDI, {new_val("ADDI")}',
            f'CHOICE + {T.GET_RESULT} -> RESULT, {new_val("RESULT")}',
            f'ADDU + {T.NEXT} -> CHOICE, {new_val("CHOICE")}',
            f'ADDI + {T.NEXT} -> CHOICE, {new_val("CHOICE")}',
            f'RESULT + {T.NEXT} -> CHOICE, {new_val("CHOICE")}',

            # We add the wait transitions because we want our circuit design to be
            # async.
            f'CHOICE + {T.WAIT} -> CHOICE, {old_val("CHOICE")}',
            f'ADDU + {T.WAIT} -> ADDU, {old_val("ADDU")}',
            f'ADDI + {T.WAIT} -> ADDI, {old_val("ADDI")}',
            f'RESULT + {T.WAIT} -> RESULT, {old_val("RESULT")}',

            # this is a hack so that we get the "new state" bit upon resetting.
            f'all + {T.RESET} -> CHOICE, {new_val("CHOICE")}'
        ]

        self.fsm = FSM(states=SESSION_STATE_NAMES,
                       input_bitwidth=SessionTransitions.bitwidth(),
                       output_bitwidth=output_bitwidth + 1, rulesList=rules)

        # expose output wires
        self.output = self.fsm()[0][:-1]
        self.new_state = self.fsm()[0][-1]
        self.state = self.fsm()[1]


    def __ilshift__(self, wire):
        self.fsm <<= wire
        return self


    def __ior__(self, wire):
        self.fsm |= wire
        return self


class SessionChoices(BitEnum):
    NULL = auto()
    ADDEND_U8 = auto()
    ADDEND_I16 = auto()
    RESULT_I16 = auto()


class AccumulatorFSM:
    def __init__(self):
        self.fsm = SessionFSM()

        # expose underlying fsm outputs
        self.new_state = self.fsm.new_state
        self.state = self.fsm.state

        # hold high to reset
        self.reset = WireVector(bitwidth=1)

        # the client module will set this to_select_an_offer.
        self.offer = WireVector(bitwidth=SessionChoices.bitwidth())

        # user logic sets this high when a value has been read
        self.received = WireVector(bitwidth=1)

        # user logic sets this high when a value is sent
        self.send = WireVector(bitwidth=1)

        self._connect_state_input()

    def _connect_state_input(self):
        C = SessionChoices
        T = SessionTransitions

        self._state_input = WireVector(T.bitwidth())
        self.fsm <<= self._state_input

        with conditional_assignment:
            with self.reset == 1:
                self._state_input |= T.RESET

            with self.offer == C.ADDEND_U8:
                self._state_input |= T.U8

            with self.offer == C.ADDEND_I16:
                self._state_input |= T.I16

            with self.offer == C.RESULT_I16:
                self._state_input |= T.GET_RESULT

            with self.received == 1:
                self._state_input |= T.NEXT

            with self.send == 1:
                self._state_input |= T.NEXT

            with otherwise:
                self._state_input |= T.WAIT


LOOP_SEQ_BITWIDTH = 2


class ClientFSM:
    def __init__(self):
        self.fsm = SessionFSM()

        # expose underlying fsm outputs
        self.new_state = self.fsm.new_state
        self.state = self.fsm.state

        # hold high to reset
        self.reset = WireVector(bitwidth=1)

        # tells us which iteration of the loop we're in
        self.loop_seq = Register(bitwidth=LOOP_SEQ_BITWIDTH)

        # which choice to take?
        self.choice = WireVector(bitwidth=SessionChoices.bitwidth())

        # user logic sets this high when a value has been read
        self.received = WireVector(bitwidth=1)

        # user logic sets this high when a value is sent
        self.send = WireVector(bitwidth=1)

        self._connect_state_input()

    def _connect_state_input(self):
        C = SessionChoices
        T = SessionTransitions

        self._state_input = WireVector(T.bitwidth())
        self.fsm <<= self._state_input

        with conditional_assignment:
            with self.reset == 1:
                self._state_input |= T.RESET

            with self.choice == C.ADDEND_U8:
                self._state_input |= T.U8

            with self.choice == C.ADDEND_I16:
                self._state_input |= T.I16

            with self.choice == C.RESULT_I16:
                self._state_input |= T.GET_RESULT

            with self.received == 1:
                self._state_input |= T.NEXT

            with self.send == 1:
                self._state_input |= T.NEXT

            with otherwise:
                self._state_input |= T.WAIT

        with conditional_assignment:
            with self.choice != C.NULL:
                self.loop_seq.next |= self.loop_seq + 1
