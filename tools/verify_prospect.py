"""Verificación visual del flujo de prospección (runtime, §5).

Abre en Chromium: la hoja de ruta, los folletos y la consola con ?prefill=
contra el server local, y deja capturas en review_out/. Falla (exit 1) si el
prefill no carga los datos reales o hay errores de consola JS.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PROSPECT_DIR = ROOT / "prospect" / "puerto-de-sagunto"
OUT = ROOT / "review_out"
SLUG = "clinica-veterinaria-namaste"
BASE = "http://127.0.0.1:8000"


def main() -> int:
    OUT.mkdir(exist_ok=True)
    prospects = json.loads((PROSPECT_DIR / "prospects.json").read_text(encoding="utf-8"))
    expected = prospects[SLUG]["values"]
    failures: list[str] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))

        page.goto((PROSPECT_DIR / "ruta.html").as_uri())
        rows = page.locator("table tr").count()
        streets = page.locator("h2").count()
        page.screenshot(path=str(OUT / "prospect-ruta.png"), full_page=False)
        print(f"ruta.html: {rows} filas, {streets} grupos de calle")
        if rows < 100:
            failures.append(f"ruta.html: solo {rows} filas (esperaba >100)")

        page.goto((PROSPECT_DIR / "folletos.html").as_uri())
        flyers = page.locator("article.flyer").count()
        qrs = page.locator("article.flyer img").count()
        page.screenshot(path=str(OUT / "prospect-folletos.png"), full_page=True)
        print(f"folletos.html: {flyers} folletos, {qrs} QRs")
        if flyers < 5 or qrs != flyers:
            failures.append(f"folletos: {flyers} folletos / {qrs} QRs")

        page.goto(f"{BASE}/?prefill={SLUG}")
        page.wait_for_selector("#formFields .field", timeout=10000)
        page.wait_for_timeout(800)  # prefill corre tras loadSectors
        got = {
            key: page.locator(f'.control[data-name="{key}"]').input_value()
            for key in ("name", "city", "phone", "address")
            if page.locator(f'.control[data-name="{key}"]').count()
        }
        sector = page.locator("#sector").input_value()
        tag = page.locator("#templateTag").text_content() or ""
        page.screenshot(path=str(OUT / "prospect-prefill.png"), full_page=False)
        print(f"prefill: sector={sector} valores={got}")
        print(f"templateTag: {tag.strip()}")
        for key, value in expected.items():
            if got.get(key, "") != value:
                failures.append(f"prefill {key}: esperaba {value!r}, hay {got.get(key)!r}")
        if "censo" not in tag:
            failures.append("falta el aviso 'datos del censo' en templateTag")
        if errors:
            failures.append(f"errores JS: {errors}")
        browser.close()
    if failures:
        print("FALLOS:\n - " + "\n - ".join(failures))
        return 1
    print("VERIFICACION VISUAL: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
