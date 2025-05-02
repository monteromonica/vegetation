# Análisis de Vegetación con Sentinel-2

Este proyecto permite descargar y analizar imágenes Sentinel-2 para el estudio de la vegetación.

## Características

- Descarga de imágenes Sentinel-2 desde AWS S3
- Descarga de imágenes Sentinel-2 desde la API de Sentinel Hub
- Cálculo de índices de vegetación (NDVI, NDWI, EVI)
- Clasificación de tipos de vegetación
- Análisis estadístico de cobertura vegetal
- Visualización de resultados

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd [NOMBRE_DEL_REPOSITORIO]
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar credenciales:
   - Copiar `.env.example` a `.env`
   - Completar las credenciales:
     - Para AWS S3 (opcional, el bucket es público)
     - Para Sentinel Hub API (opcional, si se quiere usar la API)

## Uso

### Descarga de Imágenes

#### Usando AWS S3 (recomendado)
```python
from src.sentinel_s3_download import SentinelS3Downloader

# Inicializar el downloader
downloader = SentinelS3Downloader()

# Descargar imagen
bbox = [-3.7, 40.3, -3.4, 40.6]  # [minx, miny, maxx, maxy]
time_interval = ("2024-03-15T00:00:00Z", "2024-03-16T23:59:59Z")
output_path = "data/madrid_sentinel.tif"
downloader.download_image(bbox, time_interval, output_path)
```

#### Usando la API de Sentinel Hub
```python
from src.sentinel_download import SentinelHubDownloader

# Inicializar el downloader (requiere credenciales en .env)
downloader = SentinelHubDownloader()

# Descargar imagen
bbox = [-3.7, 40.3, -3.4, 40.6]  # [minx, miny, maxx, maxy]
time_interval = ("2024-03-15T00:00:00Z", "2024-03-16T23:59:59Z")
output_path = "data/madrid_sentinel.tif"
downloader.download_image(bbox, time_interval, output_path)
```

### Análisis de Vegetación

1. Asegúrate de que el archivo de imagen Sentinel-2 esté en el directorio `data/` con el nombre `madrid_sentinel.tif`

2. Ejecutar el análisis:
```bash
python -m src.vegetation_analysis
```

El script generará:
- `data/vegetation_analysis_madrid_sentinel.png`: Visualizaciones de los índices y clasificación
- `data/vegetation_stats_madrid_sentinel.csv`: Estadísticas de la vegetación

## Estructura del Proyecto

```
.
├── data/                  # Datos e imágenes
├── src/                   # Código fuente
│   ├── sentinel_s3_download.py  # Descarga de imágenes desde S3
│   ├── sentinel_download.py     # Descarga de imágenes desde API
│   └── vegetation_analysis.py   # Análisis de vegetación
├── tests/                # Pruebas unitarias
├── .env                  # Credenciales (no subir a git)
├── .env.example          # Ejemplo de configuración
├── .gitignore           # Archivos ignorados por git
├── LICENSE              # Licencia MIT
├── README.md            # Este archivo
└── requirements.txt     # Dependencias
```

## Contribución

1. Hacer fork del repositorio
2. Crear una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Hacer commit de tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Hacer push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Referencias

- [Sentinel Hub](https://www.sentinel-hub.com/)
- [AWS Open Data Registry - Sentinel-2](https://registry.opendata.aws/sentinel-2/)
- [Documentación de Sentinel-2](https://sentinel.esa.int/web/sentinel/missions/sentinel-2) 