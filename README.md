# Price List Scraper (medicamentos)

Programa en Python para explorar páginas de medicamentos y extraer precios desde una lista de URLs que tú proporcionas.

## Requisitos

```bash
python -m pip install -r requirements.txt
```

## Formato de entrada

Archivo CSV con estas columnas:

- `url` (opcional si usas `--site` y proporcionas `nombre`)
- `nombre` (recomendado, para identificar el medicamento y construir búsquedas)
- `selector` (opcional, selector CSS simple `.clase` o `#id`)

Ejemplo (`ejemplo_entrada.csv`):

```csv
nombre,url,selector
Ibuprofeno 400,https://example.com/medicamento-1,.precio
Paracetamol 500,https://example.com/medicamento-2,
```

## Ejecución

### Modo general por URL

```bash
python scraper_medicamentos.py --input ejemplo_entrada.csv --output precios.csv
```

### Buscar en Cruz Verde (Chile)

Si en el CSV dejas vacía la columna `url` y completas `nombre`, el script arma la búsqueda automáticamente:

```bash
python scraper_medicamentos.py --input ejemplo_entrada.csv --site cruzverde --output precios_cruzverde.csv
```

También puedes definir tu plantilla de búsqueda para otro sitio:

```bash
python scraper_medicamentos.py --input ejemplo_entrada.csv --search-template "https://dominio.com/search?q={query}" --output precios.csv
```

## Salida

CSV con:

- `nombre`
- `url`
- `precio`
- `selector_usado`
- `estado` (`ok`, `sin_precio`, `error`)
- `detalle` (precio crudo o mensaje de error)

## Notas

- Si no proporcionas `selector`, el script usa heurísticas (`price`, `precio`), texto global y JSON embebido (`application/ld+json`).
- En muchos e-commerce modernos (incluyendo Cruz Verde), parte del precio puede estar en JSON de la página; por eso se agregó extracción desde JSON.
- Respeta los términos de uso, robots.txt y la legislación aplicable del sitio que consultes.
