from random import randint
from typing import Optional


def roll(d: Optional[int] = None):
    if d is None:
        d = 6

    if d < 1:
        raise ValueError("D can not be less than 1")

    return randint(1, d)
