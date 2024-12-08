from pyrtl import Input, Output, Simulation, SimulationTrace, temp_working_block

from .states import make_fsm, SessionStates, SessionTransitions


def test_fsm():
    with temp_working_block():
        input_wire = Input(bitwidth=SessionTransitions.bitwidth(), name="input")
        state = Output(bitwidth=SessionStates.bitwidth(), name="currentState")
        new_state = Output(bitwidth=1, name="newState")

        fsm_output_bitwidth = 3
        output = Output(bitwidth=fsm_output_bitwidth, name="output")

        output_values = {
                'CHOICE': 1,
                'ADDU': 3,
                'ADDI': 4,
                'RESULT': 5
        }

        session_fsm = make_fsm(output_bitwidth=3, output_values=output_values)
        session_fsm <<= input_wire

        output <<= session_fsm()[0][0:-1]
        new_state <<= session_fsm()[0][-1]  # the new_state flag is the msb

        state <<= session_fsm()[1]

        sim_trace = SimulationTrace()
        sim = Simulation(tracer=sim_trace)
        T = SessionTransitions

        input_inputs = [T.RESET, T.WAIT, T.WAIT, T.U8, T.WAIT, T.U8_TO_LOOP, T.GET_RESULT, T.WAIT, T.END, T.WAIT, T.WAIT]
        sim_inputs = {
            'input' : [x.value for x in input_inputs]
        }
        sim.step_multiple(sim_inputs)
        sim_trace.render_trace(trace_list=['input', 'currentState', 'output', 'newState'])
