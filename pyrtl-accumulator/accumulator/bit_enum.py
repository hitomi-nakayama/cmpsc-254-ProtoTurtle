from enum import auto, IntEnum

from .wires import bitwidth

class BitEnum(IntEnum):
    """An enum that starts at 0 and knows how many bits it needs to
    be represented."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> int:
        if last_values:
            return max(last_values) + 1
        return 0

    @classmethod
    def bitwidth(cls) -> int:
        return max(bitwidth(x) for x in cls)


def value(x):
    return x.value


def value_list(*args):
    return [x.value for x in args]
