"""Parseo del horario libre a ``openingHoursSpecification`` de schema.org.

El horario se escribe en texto libre ("L-V 9:00-20:00, S 9:00-14:00"). Google
entiende mejor el horario si va estructurado en el JSON-LD. Este parser es
conservador: reconoce los formatos españoles habituales y, si no entiende algo,
lo omite en vez de inventar (el JSON-LD sigue siendo válido sin horario).
"""

from __future__ import annotations

import re

# Orden de la semana en español abreviado y su día schema.org.
_DAY_ORDER = ["L", "M", "X", "J", "V", "S", "D"]
_DAY_NAME = {
    "L": "Monday",
    "M": "Tuesday",
    "X": "Wednesday",
    "J": "Thursday",
    "V": "Friday",
    "S": "Saturday",
    "D": "Sunday",
}

_TIME_RE = re.compile(
    r"(\d{1,2})(?:[:.](\d{2}))?\s*[-aà]\s*(\d{1,2})(?:[:.](\d{2}))?"
)


def _expand_days(token: str) -> list[str]:
    """'L-V' -> [L,M,X,J,V]; 'S' -> [S]; 'L,X,V' -> [L,X,V]. '' si no se entiende."""
    token = token.upper().replace(" ", "")
    if "-" in token:
        a, _, b = token.partition("-")
        if a in _DAY_ORDER and b in _DAY_ORDER:
            i, j = _DAY_ORDER.index(a), _DAY_ORDER.index(b)
            if i <= j:
                return _DAY_ORDER[i : j + 1]
        return []
    parts = [p for p in token.split(",") if p]
    if parts and all(p in _DAY_ORDER for p in parts):
        return parts
    return []


def _hhmm(hour: str, minute: str | None) -> str:
    return f"{int(hour):02d}:{minute or '00'}"


def parse_opening_hours(text: str) -> list[dict[str, object]]:
    """Devuelve una lista de OpeningHoursSpecification, o [] si no se puede parsear."""
    if not text.strip():
        return []
    specs: list[dict[str, object]] = []
    try:
        for segment in text.split(","):
            time_match = _TIME_RE.search(segment)
            if time_match is None:
                continue
            days_part = segment[: time_match.start()].strip()
            days = _expand_days(days_part)
            if not days:
                continue
            opens = _hhmm(time_match.group(1), time_match.group(2))
            closes = _hhmm(time_match.group(3), time_match.group(4))
            specs.append(
                {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": [_DAY_NAME[d] for d in days],
                    "opens": opens,
                    "closes": closes,
                }
            )
    except (ValueError, IndexError):
        return []
    return specs
