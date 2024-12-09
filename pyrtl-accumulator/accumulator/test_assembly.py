from pyrtl import Input, Output, Simulation, temp_working_block

from .assembly import Assembly


def test_assembly():
    with temp_working_block():
        assembly = Assembly()

        reset = Input(bitwidth=1, name="reset")
        assembly.reset <<= reset

        debug_output = Output(name="debug_output")
        debug_output <<= assembly.debug_output

        debug_output_valid = Output(name="debug_output_valid")
        debug_output_valid <<= assembly.debug_output_valid

        sim = Simulation()

        sim.step(provided_inputs={'reset': 1})

        for _ in range(100):
            sim.step(provided_inputs={'reset': 0})

            if sim.inspect('debug_output_valid'):
                assert 12 == sim.inspect('debug_output')
                break
        else:
            # simulation timed out
            assert False
