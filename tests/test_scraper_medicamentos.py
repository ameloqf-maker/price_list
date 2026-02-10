from scraper_medicamentos import extraer_primer_precio, normalizar_numero, parsear_precio


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
