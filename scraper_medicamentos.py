#!/usr/bin/env python3
"""Extrae precios de medicamentos a partir de una lista de URLs."""
from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from html import unescape
from pathlib import Path
from typing import Iterable, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PRICE_PATTERNS = [
    re.compile(r"(?:US\$|\$|€|MXN|COP|CLP)\s?\d{1,3}(?:[\.,\s]?\d{3})*(?:[\.,]\d{2})?", re.IGNORECASE),
    re.compile(r"\d{1,3}(?:[\.,\s]?\d{3})*(?:[\.,]\d{2})?\s?(?:USD|EUR|MXN|COP|CLP)", re.IGNORECASE),
]

TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class Resultado:
    url: str
    nombre: str
    precio: str
    selector_usado: str
    estado: str
    detalle: str


def limpiar_html_a_texto(html: str) -> str:
    texto = TAG_RE.sub(" ", html)
    return unescape(re.sub(r"\s+", " ", texto)).strip()


def normalizar_numero(valor: str) -> Optional[str]:
    limpio = re.sub(r"[^\d,\.]", "", valor)
    if not limpio:
        return None
    if limpio.count(",") > 0 and limpio.count(".") > 0:
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif limpio.count(",") > 0:
        partes = limpio.split(",")
        if len(partes[-1]) == 2:
            limpio = "".join(partes[:-1]) + "." + partes[-1]
        else:
            limpio = "".join(partes)
    else:
        partes = limpio.split(".")
        if len(partes) > 1 and len(partes[-1]) != 2:
            limpio = "".join(partes)
    try:
        return f"{Decimal(limpio):.2f}"
    except InvalidOperation:
        return None


def extraer_primer_precio(texto: str) -> Optional[str]:
    for patron in PRICE_PATTERNS:
        m = patron.search(texto)
        if m:
            return m.group(0).strip()
    return None


def _extract_by_selector_like(html: str, selector: str) -> Optional[str]:
    if not selector:
        return None
    if selector.startswith("."):
        clase = re.escape(selector[1:])
        patron = re.compile(rf"<[^>]*class=[\"'][^\"']*{clase}[^\"']*[\"'][^>]*>(.*?)</[^>]+>", re.IGNORECASE | re.DOTALL)
    elif selector.startswith("#"):
        ident = re.escape(selector[1:])
        patron = re.compile(rf"<[^>]*id=[\"']{ident}[\"'][^>]*>(.*?)</[^>]+>", re.IGNORECASE | re.DOTALL)
    else:
        return None
    m = patron.search(html)
    if not m:
        return None
    return limpiar_html_a_texto(m.group(1))


def leer_entradas(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "url" not in reader.fieldnames:
            raise ValueError("El archivo de entrada debe incluir columna: url")
        for fila in reader:
            yield {k: (v or "").strip() for k, v in fila.items()}


def descargar_html(url: str, timeout: int, user_agent: str) -> str:
    req = Request(url, headers={"User-Agent": user_agent})
    with urlopen(req, timeout=timeout) as r:  # noqa: S310
        return r.read().decode("utf-8", errors="ignore")


def parsear_precio(html: str, selector: str = "") -> tuple[Optional[str], str]:
    if selector:
        texto_sel = _extract_by_selector_like(html, selector)
        if texto_sel:
            precio = extraer_primer_precio(texto_sel)
            if precio:
                return precio, selector

    for patron, etiqueta in [
        (r"class=[\"'][^\"']*price[^\"']*[\"']", "class*=price"),
        (r"id=[\"'][^\"']*price[^\"']*[\"']", "id*=price"),
        (r"class=[\"'][^\"']*precio[^\"']*[\"']", "class*=precio"),
        (r"id=[\"'][^\"']*precio[^\"']*[\"']", "id*=precio"),
    ]:
        for m in re.finditer(rf"<[^>]*{patron}[^>]*>(.*?)</[^>]+>", html, flags=re.IGNORECASE | re.DOTALL):
            precio = extraer_primer_precio(limpiar_html_a_texto(m.group(1)))
            if precio:
                return precio, etiqueta

    precio = extraer_primer_precio(limpiar_html_a_texto(html))
    if precio:
        return precio, "texto_completo"
    return None, ""


def procesar_url(entrada: dict[str, str], timeout: int, user_agent: str) -> Resultado:
    url = entrada.get("url", "")
    nombre = entrada.get("nombre", "")
    selector = entrada.get("selector", "")
    if not url:
        return Resultado(url, nombre, "", "", "error", "URL vacía")
    try:
        html = descargar_html(url, timeout, user_agent)
        precio_crudo, selector_usado = parsear_precio(html, selector)
        if not precio_crudo:
            return Resultado(url, nombre, "", selector_usado, "sin_precio", "No se detectó precio")
        return Resultado(url, nombre, normalizar_numero(precio_crudo) or precio_crudo, selector_usado, "ok", precio_crudo)
    except (HTTPError, URLError) as exc:
        return Resultado(url, nombre, "", "", "error", f"Error HTTP: {exc}")
    except Exception as exc:  # noqa: BLE001
        return Resultado(url, nombre, "", "", "error", f"Error inesperado: {exc}")


def guardar_resultados(path: Path, resultados: Iterable[Resultado]) -> None:
    campos = ["nombre", "url", "precio", "selector_usado", "estado", "detalle"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for r in resultados:
            writer.writerow(r.__dict__)


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Explora páginas de medicamentos y extrae precios")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", default=Path("precios_extraidos.csv"), type=Path)
    p.add_argument("--timeout", default=20, type=int)
    p.add_argument("--user-agent", default="Mozilla/5.0 (compatible; PriceListBot/1.0)")
    return p


def main() -> int:
    args = construir_parser().parse_args()
    entradas = list(leer_entradas(args.input))
    resultados = [procesar_url(e, args.timeout, args.user_agent) for e in entradas]
    guardar_resultados(args.output, resultados)
    ok = sum(1 for r in resultados if r.estado == "ok")
    print(f"Proceso completado. {ok}/{len(resultados)} URLs con precio detectado. Salida: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
