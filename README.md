# Price List Scraper (medicamentos)

Programa en Python para explorar páginas de medicamentos y extraer precios desde una lista de URLs que tú proporcionas.

## Requisitos

```bash
pip install -r requirements.txt
```

## Formato de entrada

Archivo CSV con estas columnas:

- `url` (obligatoria)
- `nombre` (opcional, para identificar el medicamento)
- `selector` (opcional, selector CSS exacto del nodo donde aparece el precio)

Ejemplo (`ejemplo_entrada.csv`):

```csv
nombre,url,selector
Ibuprofeno 400,https://example.com/medicamento-1,.precio
Paracetamol 500,https://example.com/medicamento-2,
```

## Ejecución

```bash
python scraper_medicamentos.py --input ejemplo_entrada.csv --output precios.csv
```

Opciones útiles:

- `--timeout 20`
- `--user-agent "Mozilla/5.0 (...)"`

## Salida

CSV con:

- `nombre`
- `url`
- `precio`
- `selector_usado`
- `estado` (`ok`, `sin_precio`, `error`)
- `detalle` (precio crudo o mensaje de error)

## Notas

- Si no proporcionas `selector`, el script usa heurísticas (`price`, `precio`, `itemprop=price`) y luego búsqueda global por regex.
- Respeta los términos de uso, robots.txt y la legislación aplicable del sitio que consultes.
