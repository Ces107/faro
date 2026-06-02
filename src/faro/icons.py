"""Familia de iconos de línea en SVG (inline, sin CDN).

Estilo Feather/Lucide: lienzo 24x24, ``fill:none``, ``stroke:currentColor``,
grosor 1.75, extremos y uniones redondeados. El uso de una familia coherente de
iconos de línea (en vez de emojis sueltos) es el detalle que más distingue una
web "de agencia" de una amateur.

Cada valor es el INTERIOR del ``<svg>`` (paths/círculos), sin la etiqueta svg.
El color fluye por ``currentColor``.
"""

from __future__ import annotations

_DEFAULT = "pin"

# name -> inner SVG markup (24x24, stroke currentColor, fill none).
_ICONS: dict[str, str] = {
    "pin": '<path d="M12 21s-6-5.3-6-10a6 6 0 1 1 12 0c0 4.7-6 10-6 10Z"/><circle cx="12" cy="11" r="2.2"/>',
    "phone": '<path d="M6.6 4h2.4l1.2 3-1.6 1.2a11 11 0 0 0 5 5L14.8 15l3 1.2v2.4a1.6 1.6 0 0 1-1.7 1.6A15.5 15.5 0 0 1 4 6.7 1.6 1.6 0 0 1 5.6 5"/>',
    "whatsapp": '<path d="M5 19l1.3-3.6A7 7 0 1 1 9 18.2L5 19Z"/><path d="M9.2 9.4c.2 2 2.1 3.9 4.1 4.1.6 0 1.2-.5 1.3-1.1l-1.7-.8-.7.6a4 4 0 0 1-1.6-1.6l.6-.7-.8-1.7c-.6.1-1.1.7-1.1 1.3Z"/>',
    "check": '<path d="m5 12.5 4 4 10-10"/>',
    "star": '<path d="m12 4 2.3 4.7 5.2.8-3.8 3.6.9 5.1L12 16.8 7.4 18l.9-5.1L4.5 9.5l5.2-.8L12 4Z"/>',
    "clock": '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
    "calendar": '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 9h16M8 3v4M16 3v4"/>',
    "sparkle": '<path d="M12 4l1.6 4.4L18 10l-4.4 1.6L12 16l-1.6-4.4L6 10l4.4-1.6L12 4Z"/>',
    "tooth": '<path d="M8 4c-2 0-3.2 1.6-3.2 3.6 0 1.6.6 2.4.8 4 .3 2 .6 6.4 2 6.4 1.2 0 1-3 2.4-3s1.2 3 2.4 3c1.4 0 1.7-4.4 2-6.4.2-1.6.8-2.4.8-4C17.2 5.6 16 4 14 4c-1.2 0-1.5.7-2 .7s-.8-.7-2-.7Z"/>',
    "paw": '<circle cx="8" cy="8" r="1.5"/><circle cx="16" cy="8" r="1.5"/><circle cx="5.5" cy="13" r="1.5"/><circle cx="18.5" cy="13" r="1.5"/><path d="M12 21c-2.5 0-5-2-5-4.5 0-1.5 1-2.5 2-3h6c1 .5 2 1.5 2 3 0 2.5-2.5 4.5-5 4.5Z"/>',
    "scissors": '<circle cx="8.5" cy="8.5" r="2.5"/><circle cx="8.5" cy="15.5" r="2.5"/><path d="M11 8.5 21 3M11 15.5 21 21M10.5 11.5l10 0"/>',
    "fork": '<path d="M8 4v16M8 4c0 0-2 2-2 4s2 3 2 3M8 4c0 0 2 2 2 4s-2 3-2 3"/><path d="M16 4v6a2 2 0 0 1-2 2v8"/>',
    "coffee": '<path d="M6 3h12l-1.5 10.5a2 2 0 0 1-2 1.5H9.5a2 2 0 0 1-2-1.5L6 3Z"/><path d="M18 7h2a2 2 0 0 1 0 4h-2"/><path d="M4 21h16"/>',
    "bag": '<path d="M6 7h12l1 13H5L6 7Z"/><path d="M9 7V5a3 3 0 0 1 6 0v2"/>',
    "bread": '<path d="M4 11a4 4 0 0 1 4-4h8a4 4 0 0 1 0 8H5a1 1 0 0 1-1-1v-3Z"/><path d="M4 11c0-1.5 1-2.5 2-2.5"/><path d="M8 19h8v-4H8v4Z"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3-3a6 6 0 0 1-7.6 7.6L6 21a2.1 2.1 0 0 1-3-3l6.7-7.1a6 6 0 0 1 7.6-7.6l-3 3Z"/>',
    "dumbbell": '<path d="M4 14v-4M4 12h16M20 14v-4"/><rect x="2" y="10" width="3" height="4" rx="1"/><rect x="19" y="10" width="3" height="4" rx="1"/><rect x="7" y="9" width="2" height="6" rx="1"/><rect x="15" y="9" width="2" height="6" rx="1"/>',
    "pill": '<path d="m10.5 20.5-7-7a5 5 0 0 1 7-7l7 7a5 5 0 0 1-7 7Z"/><path d="m8.5 8.5 7 7"/>',
    "chart": '<polyline points="4,18 9,11 13,14 19,6"/><line x1="4" y1="20" x2="20" y2="20"/>',
    "house": '<path d="M3 10.5 12 4l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-9.5Z"/><path d="M9 21v-7h6v7"/>',
    "hammer": '<path d="m15 12 5 5-2 2-5-5"/><path d="M7.5 14.5 3 19"/><path d="M17 3 8 12l4 4 9-9a4 4 0 0 0-4-4Z"/>',
    "briefcase": '<rect x="3" y="8" width="18" height="13" rx="2"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/><line x1="3" y1="14" x2="21" y2="14"/>',
    "shield": '<path d="M12 3 4 7v6c0 4.4 3.4 8.5 8 9.5 4.6-1 8-5.1 8-9.5V7l-8-4Z"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8Z"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 4 13c0-5.5 7-12 7-12s7 6.5 7 12a7 7 0 0 1-7 7Z"/><path d="M11 20V9"/>',
    "car": '<path d="M5 17H3v-5l2-6h14l2 6v5h-2"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0Z"/><path d="M15 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0Z"/><line x1="3" y1="12" x2="21" y2="12"/>',
    "cut": '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="m8.5 8.5 7 7M8.5 15.5 21 3"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 5 9 9 9-9"/>',
    "euro": '<path d="M17 6a7 7 0 1 0 0 12"/><path d="M4 10h9M4 14h9"/>',
    "map-pin": '<path d="M12 21s-6-5.3-6-10a6 6 0 1 1 12 0c0 4.7-6 10-6 10Z"/><circle cx="12" cy="11" r="2"/>',
    "arrow-up": '<line x1="12" y1="19" x2="12" y2="5"/><polyline points="5,12 12,5 19,12"/>',
    "menu": '<line x1="3" y1="8" x2="21" y2="8"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="16" x2="21" y2="16"/>',
    "chevron-down": '<polyline points="5,9 12,16 19,9"/>',
    "quote": '<path d="M6 12h4v6H4v-6l2-6h2L6 12Z"/><path d="M14 12h4v6h-6v-6l2-6h2l-2 6Z"/>',
    "location": '<path d="M12 21s-6-5.3-6-10a6 6 0 1 1 12 0c0 4.7-6 10-6 10Z"/><circle cx="12" cy="11" r="2.5"/>',
    "key": '<circle cx="8" cy="8" r="4"/><path d="m11 11 8 8M16 16l2-2M18 18l2-2"/>',
}


def get_icon(name: str) -> str:
    """Devuelve el interior SVG del icono pedido, o el icono por defecto."""
    return _ICONS.get(name, _ICONS[_DEFAULT])


def has_icon(name: str) -> bool:
    return name in _ICONS
