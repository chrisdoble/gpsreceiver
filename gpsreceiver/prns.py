"""This module generates the GPS satellites' C/A PRNs.

The PRNs are generated by XORing the output of two linear-feedback shift
registers (LFSRs). Some documents say the second PRN is delayed by a certain
number of chips while others say the output of the second PRN is the XOR of
different stages per satellite. It turns out these approaches are equivalent.
"""

import json
from typing import Iterator

import numpy as np


def _lfsr(outputs: list[int], taps: list[int]) -> Iterator[int]:
    """Generates the output of a 10-stage linear-feedback shift register.

    ``outputs`` contains the (one-based) indices of the bits that are used to
    calculate the LFSR's output on each iteration, e.g. if ``outputs = [1, 2]``
    the output would be ``bits[0] ^ bits[1]``.

    Similarly, ``taps`` contains the (one-based) indices of the bits that are
    used to calculate the LFSR's leftmost bit on each iteration.

    The LFSR is seeded with ones.

    One-based indices are used to better match the GPS spec.
    """
    bits = [1 for _ in range(10)]

    while True:
        output = sum([bits[i - 1] for i in outputs]) % 2
        yield output

        feedback = sum(bits[i - 1] for i in taps) % 2

        for i in range(9, 0, -1):
            bits[i] = bits[i - 1]

        bits[0] = feedback


# The taps used to generate each satellite's PRN, indexed by satellite ID.
#
# Taken from Table 3-Ia in the GPS spec[1].
#
# 1: https://www.gps.gov/technical/icwg/IS-GPS-200L.pdf
_prn_taps = [
    [2, 6],
    [3, 7],
    [4, 8],
    [5, 9],
    [1, 9],
    [2, 10],
    [1, 8],
    [2, 9],
    [3, 10],
    [2, 3],
    [3, 4],
    [5, 6],
    [6, 7],
    [7, 8],
    [8, 9],
    [9, 10],
    [1, 4],
    [2, 5],
    [3, 6],
    [4, 7],
    [5, 8],
    [6, 9],
    [1, 3],
    [4, 6],
    [5, 7],
    [6, 8],
    [7, 9],
    [8, 10],
    [1, 6],
    [2, 7],
    [3, 8],
    [4, 9],
]

# The PRNS of all GPS satellites, indexed by satellite ID.
PRNS: list[np.ndarray] = []

for taps in _prn_taps:
    g1 = _lfsr([10], [3, 10])
    g2 = _lfsr(taps, [2, 3, 6, 8, 9, 10])
    prn = np.empty(1023, np.float32)
    for i in range(1023):
        prn[i] = (next(g1) + next(g2)) % 2
    PRNS.append(prn)
