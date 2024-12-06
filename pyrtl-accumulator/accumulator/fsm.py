"""
fsm.py by Tejas Vissapragada
"""

from pyrtl import PyrtlError, WireVector, Register, MemBlock, conditional_assignment, otherwise
from pyrtl.rtllib.muxes import sparse_mux
from pyrtl.corecircuits import concat, as_wires
from pyrtl.simulation import Simulation
from pyrtl.helperfuncs import probe
from enum import Enum
from lark import Lark, Transformer
from abc import ABC, abstractmethod
import math

#Grammar for Rules
#state + input -> state
#STRING " + " INT " -> " STRING

class RuleTransformer(Transformer):
    def __init__(self, input_bitwidth, states):
        self.input_bitwidth = input_bitwidth
        self.states = states

    def state(self, wordList):
        return wordList[0]

    def input(self, intList):
        try:
            return int(intList[0])
        except ValueError:
            return intList[0]

    def output(self, outList):
        return int(outList[0])

    def start(self, rule):
        if rule[0] == "all" or rule[1] == "all":
            if rule[0] == "all":
                rulesUpdate = {}
                outputsUpdate = {}
                for state in self.states:
                    stateInBits = self.states.index(state)
                    key = (stateInBits << self.input_bitwidth) | rule[1]
                    rulesUpdate.update({key : self.states.index(rule[2])})
                    outputsUpdate.update({key : rule[3]})

                return [rulesUpdate, outputsUpdate]

            elif rule[1] == "all":
                rulesUpdate = {}
                outputsUpdate = {}
                for i in range(2**self.input_bitwidth - 1):
                    stateInBits = self.states.index(rule[0])
                    key = (stateInBits << self.input_bitwidth) | i
                    rulesUpdate.update({key : self.states.index(rule[2])})
                    outputsUpdate.update({key : rule[3]})

                return [rulesUpdate, outputsUpdate]
        else:
            stateInBits = self.states.index(rule[0])
            key = (stateInBits << self.input_bitwidth) | rule[1]
            return [{key : self.states.index(rule[2])}, {key : rule[3]}]


class FSM:
    def __init__(self, input_bitwidth, output_bitwidth, states, rulesList, reset=0, enable=1):
        self.reset_wire = WireVector(bitwidth=1)
        self.reset_wire <<= reset
        self.enable_wire = WireVector(bitwidth=1)
        self.enable_wire <<= enable
        self.input_wire = WireVector(bitwidth=input_bitwidth)
        self.state_bitwidth = math.floor(math.log(len(states))/math.log(2)) + 1
        self.input_bitwidth = input_bitwidth
        self.state = Register(bitwidth=self.state_bitwidth)
        self.output = Register(bitwidth=output_bitwidth)
        self.stateList = states

        rule_grammar = '''
            start : state " + " input " -> " state ", " output
            state : WORD
            input : INT | WORD
            output : INT
            %import common.INT
            %import common.WORD
        '''
        rule_parser = Lark(rule_grammar)

        self.rules = {}
        self.outputs = {}
        for rule in rulesList:
            rule_tree = rule_parser.parse(rule)
            newRules = RuleTransformer(input_bitwidth, states).transform(rule_tree)
            self.rules.update(newRules[0])
            self.outputs.update(newRules[1])

    def __ilshift__(self, wire):
        # probe(self.input_wire)
        #condition = as_wires(self.reset)
        self.input_wire <<= wire

        with conditional_assignment:
            with self.enable_wire == 0:
                self.state.next |= self.state
                self.output.next |= 0
            with self.reset_wire:
                self.state.next |= 0
                self.output.next |= 0
            with otherwise:
                self.state.next |= sparse_mux(concat(self.state, self.input_wire), self.rules)
                self.output.next |= sparse_mux(concat(self.state, self.input_wire), self.outputs)
        return self

    def __ior__(self, wire):
        if len(wire) != self.input_bitwidth:
            raise PyrtlError("Invalid Input Bitwidth")
        self.input_wire |= wire
        with self.enable_wire == 0:
            self.state.next |= self.state
            self.output.next |= 0
        with self.reset_wire:
            self.state.next |= 0
            self.output.next |= 0
        with otherwise:
            self.state.next |= sparse_mux(concat(self.state, self.input_wire), self.rules)
            self.output.next |= sparse_mux(concat(self.state, self.input_wire), self.outputs)
        return self

    def __call__(self):
        return [self.output, self.state]
