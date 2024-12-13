# ProtoTurtle
Code for the final project in CMPSC 254 Fall 2024 done by Hitomi Nakayama and Sarah Canto

## prototurtle-accumulator directory
Contains the implementation of the accumulator program written in our proposed DSL

## pyrtl-accumulator directory
Contains the PyRTL implementation of the FSM and logic that represents an equivalent accumulator program as the one written in ProtoTurtle as found the prototurtle-accumulator directory. This implementation uses pipenv for python version management.

## session-types-accumulator directory
Contains the initial implementation of our accumulator program written in Rust using the session-types library.

## session-types-choice directory
Contains the code written in Rust using the session-types library that represents the sign extender.

## session-types-dpa directory
Contains the code written in Rust using the session-types library that represent the DPA.

## session-types-handshake directory
Contains the code written in Rust using the session-types library that represents an AXI style valid ready handshake.

## session-types-test directory
Contains the code for our initially developed simple example using the Rust session-types library. It just represents a Client/Server communication.
