"""Tests del parser de horarios a schema.org."""

from __future__ import annotations

from faro.hours import parse_opening_hours


def test_simple_range() -> None:
    specs = parse_opening_hours("L-V 9:00-20:00")
    assert len(specs) == 1
    assert specs[0]["dayOfWeek"] == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    assert specs[0]["opens"] == "09:00"
    assert specs[0]["closes"] == "20:00"


def test_two_segments() -> None:
    specs = parse_opening_hours("L-V 9:00-20:00, S 9:00-14:00")
    assert len(specs) == 2
    assert specs[1]["dayOfWeek"] == ["Saturday"]
    assert specs[1]["closes"] == "14:00"


def test_hours_without_minutes() -> None:
    specs = parse_opening_hours("L-D 8-23")
    assert specs[0]["opens"] == "08:00"
    assert specs[0]["closes"] == "23:00"
    assert specs[0]["dayOfWeek"][-1] == "Sunday"


def test_comma_separated_day_list() -> None:
    # Antes se descartaban días silenciosamente ('L,X,V' -> solo viernes).
    specs = parse_opening_hours("L,X,V 9:00-14:00")
    assert len(specs) == 1
    assert specs[0]["dayOfWeek"] == ["Monday", "Wednesday", "Friday"]


def test_mixed_range_and_single() -> None:
    specs = parse_opening_hours("L-V 9-18, S 10-14")
    assert specs[0]["dayOfWeek"] == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    assert specs[1]["dayOfWeek"] == ["Saturday"]


def test_split_shift_keeps_both_segments() -> None:
    # Turno partido: el segundo rango sin día hereda los días del primero.
    specs = parse_opening_hours("L-V 9:00-14:00, 17:00-20:00")
    assert len(specs) == 2
    assert specs[0]["opens"] == "09:00" and specs[0]["closes"] == "14:00"
    assert specs[1]["opens"] == "17:00" and specs[1]["closes"] == "20:00"
    assert specs[1]["dayOfWeek"] == specs[0]["dayOfWeek"]  # mismos días heredados


def test_unparseable_returns_empty() -> None:
    assert parse_opening_hours("abrimos cuando podemos") == []
    assert parse_opening_hours("") == []
