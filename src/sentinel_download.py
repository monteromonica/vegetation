import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class SentinelHubDownloader:
    def __init__(self):
        """Inicializa el downloader con las credenciales de Sentinel Hub"""
        self.client_id = os.getenv('SENTINEL_CLIENT_ID')
        self.client_secret = os.getenv('SENTINEL_CLIENT_SECRET')
        if not self.client_id or not self.client_secret:
            raise ValueError("Las credenciales de Sentinel Hub no están configuradas. Por favor, configura las variables de entorno SENTINEL_CLIENT_ID y SENTINEL_CLIENT_SECRET.")
        self.token = None
        self.base_url = "https://services.sentinel-hub.com/api/v1/process"
        
    def get_token(self):
        """Obtiene el token de autenticación"""
        url = "https://services.sentinel-hub.com/oauth/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(url, data=data)
        self.token = response.json()["access_token"]
        return self.token
        
    def download_image(self, bbox, time_interval, output_path, 
                      resolution=10, maxcc=0.3):
        """
        Descarga una imagen de Sentinel-2
        
        Parámetros:
        -----------
        bbox : list
            [minx, miny, maxx, maxy] en coordenadas WGS84
        time_interval : tuple
            (start_date, end_date) en formato ISO-8601
        output_path : str
            Ruta donde guardar la imagen
        resolution : int
            Resolución en metros
        maxcc : float
            Máxima cobertura de nubes permitida (0-1)
        """
        if not self.token:
            self.get_token()
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Configuración de la solicitud
        request = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {
                        "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                    }
                },
                "data": [{
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": time_interval[0],
                            "to": time_interval[1]
                        },
                        "maxCloudCoverage": maxcc
                    }
                }]
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [{
                    "identifier": "default",
                    "format": {
                        "type": "image/tiff"
                    }
                }]
            },
            "evalscript": """
                //VERSION=3
                function setup() {
                    return {
                        input: ["B02", "B03", "B04", "B08"],
                        output: { bands: 4 }
                    };
                }
                function evaluatePixel(sample) {
                    return [sample.B04, sample.B03, sample.B02, sample.B08];
                }
            """
        }
        
        # Realizar la solicitud
        response = requests.post(
            self.base_url,
            headers=headers,
            json=request
        )
        
        # Guardar la imagen
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Imagen guardada en {output_path}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

def main():
    # Crear instancia del downloader
    downloader = SentinelHubDownloader()
    
    # Coordenadas para el centro de Madrid
    bbox = [-3.7038, 40.4168, -3.6693, 40.4378]  # [minx, miny, maxx, maxy]
    
    # Fecha de hoy y hace 30 días en formato ISO-8601
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    time_interval = (
        start_date.strftime("%Y-%m-%dT00:00:00Z"),
        end_date.strftime("%Y-%m-%dT23:59:59Z")
    )
    
    # Descargar la imagen
    output_path = "madrid_sentinel.tif"
    downloader.download_image(
        bbox=bbox,
        time_interval=time_interval,
        output_path=output_path,
        maxcc=0.1  # Solo imágenes con menos del 10% de nubes
    )

if __name__ == "__main__":
    main() 