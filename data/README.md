# Datos y Resultados

Este directorio contiene las imágenes satelitales y los resultados de los análisis realizados.

## Imágenes Originales

- `madrid_sentinel.tif` (278KB)
  - Imagen Sentinel-2 de Madrid
  - Fecha: 2024-03-15
  - Resolución: 10m
  - Bandas: B02 (azul), B03 (verde), B04 (rojo), B08 (NIR)
  - Área: Centro de Madrid

- `madrid_sentinel_20240315.tif` (920MB)
  - Imagen Sentinel-2 de Madrid de mayor resolución
  - Fecha: 2024-03-15
  - Resolución: 10m
  - Bandas: B02 (azul), B03 (verde), B04 (rojo), B08 (NIR)
  - Área: Tile completo 30TYN que cubre Madrid

## Resultados de Análisis

### Análisis de Vegetación

- `vegetation_analysis_madrid_sentinel.png` (1.2MB)
  - Visualización de índices de vegetación para la imagen original
  - Incluye NDVI, NDWI, EVI y clasificación de vegetación
  - Generado el 2024-03-15

- `vegetation_analysis_madrid_sentinel_20240315.png` (27MB)
  - Visualización de índices de vegetación para la imagen de alta resolución
  - Incluye NDVI, NDWI, EVI y clasificación de vegetación
  - Generado el 2024-03-15

### Estadísticas

- `vegetation_stats_madrid_sentinel.csv`
  - Estadísticas de vegetación para la imagen original
  - Incluye porcentajes de cobertura vegetal, agua y suelo desnudo

- `vegetation_stats_madrid_sentinel_20240315.csv`
  - Estadísticas de vegetación para la imagen de alta resolución
  - Incluye porcentajes de cobertura vegetal, agua y suelo desnudo

## Notas

- Las imágenes `.tif` son archivos grandes y no se incluyen en el repositorio de GitHub
- Los archivos `.png` y `.csv` son los resultados del análisis y se incluyen para referencia
- Para reproducir los análisis, se recomienda descargar las imágenes originales desde:
  - [Sentinel Hub](https://www.sentinel-hub.com/)
  - [AWS Open Data Registry - Sentinel-2](https://registry.opendata.aws/sentinel-2/) 