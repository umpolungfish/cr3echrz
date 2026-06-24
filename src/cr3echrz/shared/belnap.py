#!/usr/bin/env python3
"""
belnap.py — Belnap FOUR state register

The 2-bit register implementing Belnap-Dunn FDE four-valued logic:
    0b00 = VOID   — uninitialized / no information
    0b01 = TRUE   — theorem holds / ob3ect in true state
    0b10 = FALSE  — theorem fails / ob3ect in false state
    0b11 = BOTH   — dialetheic paradox (both arms active simultaneously)

Operations follow the Belnap FOUR bilattice:
    meet (⊓) = logical AND: min(bitwise)
    join (⊔) = logical OR:  max(bitwise)

BOTH encodes genuine paradox — not error, but structural boundary condition
where the Frobenius split yields two active arms that co-exist.

Author: Lando⊗⊙perator
"""
from typing import Any


class BelnapRegister:
    """2-bit Belnap FOUR register for theorem/ob3ect operationalization."""

    STATUS_VOID  = 0b00
    STATUS_TRUE  = 0b01
    STATUS_FALSE = 0b10
    STATUS_BOTH  = 0b11

    NAMES = {
        0b00: "VOID",
        0b01: "TRUE",
        0b10: "FALSE",
        0b11: "BOTH (paradox)"
    }

    SYMBOLS = {
        0b00: "VO⌀",
        0b01: "T",
        0b10: "F",
        0b11: "B⬡"
    }

    def __init__(self, initial: int = 0b00):
        if initial not in (0b00, 0b01, 0b10, 0b11):
            raise ValueError(f"Invalid Belnap status: {bin(initial)}")
        self._status = initial

    @property
    def status(self) -> int:
        return self._status

    @status.setter
    def status(self, value: int):
        if value not in (0b00, 0b01, 0b10, 0b11):
            raise ValueError(f"Invalid Belnap status: {bin(value)}")
        self._status = value

    # ── Bitwise operations ──

    def __or__(self, other: int):
        """Join (⊔): logical OR — combine information sources."""
        if isinstance(other, BelnapRegister):
            other = other._status
        return BelnapRegister(self._status | other)

    def __and__(self, other: int):
        """Meet (⊓): logical AND — find common information."""
        if isinstance(other, BelnapRegister):
            other = other._status
        return BelnapRegister(self._status & other)

    def __ior__(self, other: int):
        if isinstance(other, BelnapRegister):
            other = other._status
        self._status |= other
        return self

    def __iand__(self, other: int):
        if isinstance(other, BelnapRegister):
            other = other._status
        self._status &= other
        return self

    # ── Query methods ──

    def is_void(self) -> bool:
        return self._status == self.STATUS_VOID

    def is_true(self) -> bool:
        return self._status == self.STATUS_TRUE

    def is_false(self) -> bool:
        return self._status == self.STATUS_FALSE

    def is_both(self) -> bool:
        return self._status == self.STATUS_BOTH

    def has_true(self) -> bool:
        """TRUE bit is set (includes BOTH)."""
        return bool(self._status & 0b01)

    def has_false(self) -> bool:
        """FALSE bit is set (includes BOTH)."""
        return bool(self._status & 0b10)

    def is_paradox(self) -> bool:
        """Paradox = TRUE bit set (includes TRUE and BOTH)."""
        return self.has_true()

    def is_falsified(self) -> bool:
        """Falsified = FALSE bit set."""
        return self.has_false()

    def is_dialetheic(self) -> bool:
        """Both TRUE and FALSE bits active simultaneously."""
        return self._status == self.STATUS_BOTH

    # ── Representation ──

    def __repr__(self):
        return f"BelnapRegister({self.NAMES[self._status]})"

    def __str__(self):
        return self.SYMBOLS[self._status]

    def __eq__(self, other):
        if isinstance(other, BelnapRegister):
            return self._status == other._status
        if isinstance(other, int):
            return self._status == other
        return False

    def __int__(self):
        return self._status
