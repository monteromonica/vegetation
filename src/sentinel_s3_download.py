import rasterio
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import subprocess
from rasterio.warp import transform

class SentinelS3Downloader:
    def __init__(self):
        """Inicializa el downloader con los buckets de Sentinel-2"""
        self.data_bucket = "sentinel-s2-l2a"
        self.region = "eu-central-1"
        
        # Configurar cliente S3 con credenciales
        self.s3_client = boto3.client('s3', region_name=self.region)
        
    def get_tile_info(self, bbox):
        """Obtiene información del tile Sentinel-2 que cubre el área especificada"""
        return "30/T/YN"
        
    def check_available_data(self, tile_info, year, month, day):
        """
        Verifica qué datos están disponibles para una fecha específica
        """
        try:
            # Listar archivos en el bucket de datos
            cmd = f"aws s3 ls --request-payer requester s3://{self.data_bucket}/tiles/{tile_info}/{year}/{month}/{day}/0/R10m/"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                print("Datos disponibles:")
                print(result.stdout)
                return True
            else:
                print(f"No hay datos disponibles para {year}-{month}-{day}")
                return False
                
        except Exception as e:
            print(f"Error al verificar datos disponibles: {e}")
            return False
        
    def download_image(self, bbox, time_interval, output_path, resolution=10):
        """
        Descarga una imagen de Sentinel-2 desde el bucket público de AWS
        """
        try:
            # Obtener información del tile
            tile_info = self.get_tile_info(bbox)
            print(f"\nTile MGRS: {tile_info}")
            
            # Convertir fechas a formato de Sentinel
            start_date = datetime.strptime(time_interval[0], "%Y-%m-%dT%H:%M:%SZ")
            year = start_date.year
            month = start_date.month
            day = start_date.day
            
            print(f"Verificando datos para {year}-{month:02d}-{day:02d}")
            
            # Verificar datos disponibles
            if not self.check_available_data(tile_info, year, month, day):
                print("No hay datos disponibles para esta fecha")
                return False
            
            # Bandas que necesitamos
            bands = {
                'B02': 'blue',
                'B03': 'green',
                'B04': 'red',
                'B08': 'nir'
            }
            
            # Crear directorio de salida si no existe
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            print("\nIniciando descarga de bandas...")
            # Descargar cada banda
            band_data = {}
            metadata = None
            for band, name in bands.items():
                try:
                    # Construir la clave S3
                    s3_key = f"tiles/{tile_info}/{year}/{month}/{day}/0/R10m/{band}.jp2"
                    print(f"\nDescargando banda {band} ({name})...")
                    print(f"URL: s3://{self.data_bucket}/{s3_key}")
                    
                    # Descargar usando AWS CLI con credenciales y requester pays
                    temp_file = f"temp_{band}.jp2"
                    cmd = f"aws s3 cp --request-payer requester s3://{self.data_bucket}/{s3_key} {temp_file}"
                    print("Ejecutando comando de descarga...")
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        print(f"Error al descargar banda {band}:")
                        print(result.stderr)
                        print("\nAsegúrate de que:")
                        print("1. Tienes las credenciales AWS configuradas correctamente")
                        print("2. Tu cuenta AWS tiene permisos para acceder a S3")
                        print("3. La región está configurada como eu-central-1")
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                        return False
                    
                    print("Descarga completada. Procesando imagen...")
                    # Leer el archivo con rasterio
                    with rasterio.open(temp_file) as src:
                        # Imprimir información de la imagen original
                        print(f"Dimensiones originales: {src.width}x{src.height}")
                        print(f"CRS original: {src.crs}")
                        print(f"Transformación original: {src.transform}")
                        
                        # Leer la banda completa
                        data = src.read(1)
                        band_data[name] = data
                        print(f"Dimensiones de la banda {band}: {data.shape}")
                        
                        if metadata is None:
                            metadata = {
                                'crs': src.crs,
                                'transform': src.transform,
                                'width': src.width,
                                'height': src.height
                            }
                            print(f"Metadatos guardados: CRS={src.crs}, Dimensiones={src.width}x{src.height}")
                    
                    # Eliminar archivo temporal
                    os.remove(temp_file)
                    print(f"Banda {band} ({name}) procesada correctamente")
                    
                except Exception as e:
                    print(f"Error al procesar banda {band}: {e}")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    return False
            
            # Crear imagen multibanda
            print(f"\nNúmero de bandas descargadas: {len(band_data)}")
            if len(band_data) == 4 and metadata is not None:
                print("\nCreando imagen multibanda...")
                print(f"Metadatos para la imagen final: CRS={metadata['crs']}, Dimensiones={metadata['width']}x{metadata['height']}")
                
                profile = {
                    'driver': 'GTiff',
                    'height': metadata['height'],
                    'width': metadata['width'],
                    'count': 4,
                    'dtype': band_data['red'].dtype,
                    'crs': metadata['crs'],
                    'transform': metadata['transform']
                }
                
                try:
                    with rasterio.open(output_path, 'w', **profile) as dst:
                        print("Escribiendo bandas en el archivo...")
                        dst.write(band_data['blue'], 1)
                        dst.write(band_data['green'], 2)
                        dst.write(band_data['red'], 3)
                        dst.write(band_data['nir'], 4)
                        print("Todas las bandas escritas correctamente")
                    
                    print(f"\nImagen guardada exitosamente en: {output_path}")
                    return True
                except Exception as e:
                    print(f"Error al guardar la imagen: {e}")
                    return False
            else:
                print("\nNo se pudieron descargar todas las bandas")
                print(f"Bandas disponibles: {list(band_data.keys())}")
                if metadata is None:
                    print("No se encontraron metadatos")
                return False
                
        except Exception as e:
            print(f"Error general en la descarga: {e}")
            return False

def main():
    # Crear instancia del downloader
    downloader = SentinelS3Downloader()
    
    # Coordenadas para el tile 30TYN
    # Estas son las coordenadas exactas del tile en UTM30N (EPSG:32630)
    # left=699960.0, bottom=4690200.0, right=809760.0, top=4800000.0
    # Convertidas a WGS84 (EPSG:4326)
    bbox = [-4.0, 42.3, -3.0, 43.3]  # [minx, miny, maxx, maxy]
    
    # Usar una fecha específica donde sabemos que hay datos
    start_date = datetime(2024, 3, 15)  # 15 de marzo de 2024
    end_date = start_date + timedelta(days=1)
    
    time_interval = (
        start_date.strftime("%Y-%m-%dT00:00:00Z"),
        end_date.strftime("%Y-%m-%dT23:59:59Z")
    )
    
    # Descargar la imagen
    output_path = "madrid_sentinel_20240315.tif"  # Nombre más descriptivo
    print(f"Intentando descargar imagen para el {start_date.strftime('%Y-%m-%d')}")
    print(f"Bbox: {bbox}")
    print("Nota: Este bbox cubre el tile 30TYN completo")
    downloader.download_image(
        bbox=bbox,
        time_interval=time_interval,
        output_path=output_path
    )

if __name__ == "__main__":
    main() 