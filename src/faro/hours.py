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

# Captura "<días> <hora>-<hora>" como una unidad, para no romper las listas de
# días separadas por coma ("L,X,V 9-14") al trocear el texto por comas.
_SEGMENT_RE = re.compile(
    r"([LMXJVSD](?:\s*[-,]\s*[LMXJVSD])*)\s+"
    r"(\d{1,2})(?:[:.](\d{2}))?\s*[-aà]\s*(\d{1,2})(?:[:.](\d{2}))?",
    re.IGNORECASE,
)


def _expand_days(token: str) -> list[str]:
    """'L-V' -> [L,M,X,J,V]; 'S' -> [S]; 'L,X,V' -> [L,X,V]; 'L-V,S' -> [L..V,S].

    Devuelve [] si algún tramo no se entiende.
    """
    token = token.upper().replace(" ", "")
    out: list[str] = []
    for part in token.split(","):
        if not part:
            continue
        if "-" in part:
            a, _, b = part.partition("-")
            if a not in _DAY_ORDER or b not in _DAY_ORDER:
                return []
            i, j = _DAY_ORDER.index(a), _DAY_ORDER.index(b)
            if i > j:
                return []
            out.extend(_DAY_ORDER[i : j + 1])
        elif part in _DAY_ORDER:
            out.append(part)
        else:
            return []
    return out


def _hhmm(hour: str, minute: str | None) -> str:
    return f"{int(hour):02d}:{minute or '00'}"


def parse_opening_hours(text: str) -> list[dict[str, object]]:
    """Devuelve una lista de OpeningHoursSpecification, o [] si no se puede parsear."""
    if not text.strip():
        return []
    specs: list[dict[str, object]] = []
    try:
        for match in _SEGMENT_RE.finditer(text):
            days = _expand_days(match.group(1))
            if not days:
                continue
            specs.append(
                {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": [_DAY_NAME[d] for d in days],
                    "opens": _hhmm(match.group(2), match.group(3)),
                    "closes": _hhmm(match.group(4), match.group(5)),
                }
            )
    except (ValueError, IndexError):
        return []
    return specs
