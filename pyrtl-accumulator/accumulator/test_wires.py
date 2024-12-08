from .wires import bitwidth

def test_bitwidth_0():
    assert 1 == bitwidth(0)

def test_bitwidth_255():
    assert 8 == bitwidth(255)

def test_bitwidth_256():
    assert 9 == bitwidth(256)
