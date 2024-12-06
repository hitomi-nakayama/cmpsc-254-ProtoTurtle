from enum import auto, Enum

class OneHotEnum(Enum):
    """An Enum which counts upward using one-hot values."""
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return 2 ** count


class SessionStates(OneHotEnum):
    LOOP_CHOICE = auto()
    DATATYPE_CHOICE = auto()
    ADDEND_U8 = auto()
    ADDEND_I16 = auto()
    RESULT = auto()


class SessionTransitions(OneHotEnum):
    LOOP_YES = auto()
    U8 = auto()
    U8_TO_LOOP = auto()
    I16 = auto()
    I16_TO_LOOP = auto()
    LOOP_NO = auto()
    END = auto()


def make_session_transition_table():
    global SESSION_TRANSITION_TABLE

    S = SessionStates
    T = SessionTransitions
    return [
        (),
        (),
        (),
        (),
    ]

SESSION_TRANSITION_TABLE = make_session_transition_table()
