from enum import auto, Enum

class OneHotEnum(Enum):
    """An Enum which counts upward using one-hot values."""
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return 2 ** count
