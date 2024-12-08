from io import StringIO

from pyrtl import Simulation

def check_step_multiple(provided_inputs={}, expected_outputs={}):
    """Create a simulation and check the report file if an error occured."""
    sim = Simulation()
    report = StringIO()

    sim.step_multiple(provided_inputs=provided_inputs,
                      expected_outputs=expected_outputs,
                      file=report)

    check_report_error(report)



def check_report_error(report_file):
    """Raise an exception if the report file contains an error."""
    report_file.seek(0)
    report_file_text = report_file.read()
    if report_file_text.startswith("Unexpected output"):
        raise RuntimeError(report_file_text)
