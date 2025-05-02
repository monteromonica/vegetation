# Análisis de Vegetación con Sentinel-2

Este proyecto permite descargar y analizar imágenes Sentinel-2 para el estudio de la vegetación.

## Características

- Descarga de imágenes Sentinel-2 desde AWS S3
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
   - Completar las credenciales de AWS S3

## Uso

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
│   ├── sentinel_s3_download.py  # Descarga de imágenes
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