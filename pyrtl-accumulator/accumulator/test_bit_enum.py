from .bit_enum import auto, BitEnum

def test_bit_enum_start():
    class TestEnum(BitEnum):
        START = auto()

    assert 0 == TestEnum.START


def test_bit_enum_second():
    class TestEnum(BitEnum):
        FIRST = auto()
        SECOND = auto()

    assert 1 == TestEnum.SECOND


def test_bit_enum_skipped():
    class TestEnum(BitEnum):
        START = auto()
        NEXT = 10
        AFTER = auto()

    assert 11 == TestEnum.AFTER


def test_bit_enum_bitwidth_1():
    class TestEnum(BitEnum):
        FIRST = 1

    assert 1 == TestEnum.bitwidth()

def test_bit_enum_bitwidth_1():
    class TestEnum(BitEnum):
        FIRST = 256

    assert 9 == TestEnum.bitwidth()
