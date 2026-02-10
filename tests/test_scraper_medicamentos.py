from scraper_medicamentos import (
    construir_url_busqueda,
    extraer_primer_precio,
    normalizar_numero,
    parsear_precio,
)


def test_extraer_primer_precio():
    texto = "Oferta especial: $ 1,234.50 por caja"
    assert extraer_primer_precio(texto) == "$ 1,234.50"


def test_normalizar_numero():
    assert normalizar_numero("$ 1,234.50") == "1234.50"
    assert normalizar_numero("1.234,50 EUR") == "1234.50"


def test_parsear_precio_por_selector():
    html = "<html><body><span class='precio'>$ 999.99</span></body></html>"
    precio, usado = parsear_precio(html, ".precio")
    assert precio == "$ 999.99"
    assert usado == ".precio"


def test_parsear_precio_por_json_ld():
    html = """
    <html><head>
    <script type="application/ld+json">
    {"@context":"https://schema.org","offers":{"price":"12345"}}
    </script>
    </head><body></body></html>
    """
    precio, usado = parsear_precio(html)
    assert precio == "12345.00"
    assert usado == "json"


def test_construir_url_busqueda_cruzverde():
    url = construir_url_busqueda("paracetamol 500", site="cruzverde")
    assert url == "https://www.cruzverde.cl/search?q=paracetamol+500"
