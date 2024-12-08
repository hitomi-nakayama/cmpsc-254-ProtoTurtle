import math

def bitwidth(n: int) -> int:
    """Return the number of bits required to represent n."""
    if n < 0:
        raise NotImplementedError("Support for negative BitEnum values"
                                  " not yet implemented")

    if n == 0:
        return 1

    return int(math.log(n) / math.log(2)) + 1
