import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import dask.array as da
from skimage import exposure
import cv2
from osgeo import gdal

class SatelliteImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.dataset = None
        self.image_data = None
        
    def load_image(self):
        """Carga la imagen satelital usando rasterio"""
        self.dataset = rasterio.open(self.image_path)
        self.image_data = self.dataset.read()
        return self.image_data
    
    def apply_atmospheric_correction(self):
        """Aplica una corrección atmosférica básica usando histogram matching"""
        if self.image_data is None:
            raise ValueError("Primero debe cargar la imagen")
            
        corrected_data = np.zeros_like(self.image_data)
        for band in range(self.image_data.shape[0]):
            # Normalización de la banda
            band_data = self.image_data[band]
            band_data = exposure.equalize_hist(band_data)
            corrected_data[band] = band_data
            
        return corrected_data
    
    def apply_geometric_correction(self):
        """Aplica una corrección geométrica básica"""
        if self.image_data is None:
            raise ValueError("Primero debe cargar la imagen")
            
        # Aquí se implementaría la corrección geométrica real
        # Por ahora solo retornamos la imagen original
        return self.image_data
    
    def fuse_multispectral(self, method='pca'):
        """Fusión de bandas multiespectrales"""
        if self.image_data is None:
            raise ValueError("Primero debe cargar la imagen")
            
        if method == 'pca':
            # Convertir a formato adecuado para PCA
            reshaped_data = self.image_data.reshape(self.image_data.shape[0], -1).T
            # Aplicar PCA
            mean = np.mean(reshaped_data, axis=0)
            centered_data = reshaped_data - mean
            cov_matrix = np.cov(centered_data.T)
            eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
            
            # Ordenar los componentes principales por valor propio
            idx = eigenvalues.argsort()[::-1]
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]
            
            # Proyectar en los componentes principales
            projected = np.dot(centered_data, eigenvectors)
            
            # Tomar el primer componente principal
            first_component = projected[:, 0]
            
            # Normalizar y escalar a uint8
            first_component = (first_component - first_component.min()) / (first_component.max() - first_component.min())
            first_component = (first_component * 255).astype(np.uint8)
            
            # Reconstruir la imagen
            fused_image = first_component.reshape(self.image_data.shape[1:])
            return fused_image
        else:
            raise ValueError(f"Método de fusión {method} no soportado")
    
    def process_distributed(self):
        """Procesamiento distribuido usando Dask"""
        if self.image_data is None:
            raise ValueError("Primero debe cargar la imagen")
            
        # Convertir a array Dask
        dask_array = da.from_array(self.image_data, chunks=(1, 1000, 1000))
        
        # Aplicar operaciones en paralelo
        corrected = dask_array.map_blocks(
            lambda x: exposure.equalize_hist(x),
            dtype=self.image_data.dtype
        )
        
        return corrected.compute()

def main():
    # Usar la imagen descargada
    processor = SatelliteImageProcessor('madrid_sentinel.tif')
    
    # Cargar imagen
    image_data = processor.load_image()
    print(f"Dimensiones de la imagen: {image_data.shape}")
    print(f"Tipo de datos: {image_data.dtype}")
    
    # Aplicar correcciones
    print("Aplicando corrección atmosférica...")
    atmospheric_corrected = processor.apply_atmospheric_correction()
    
    print("Aplicando corrección geométrica...")
    geometric_corrected = processor.apply_geometric_correction()
    
    # Fusión multiespectral
    print("Realizando fusión multiespectral...")
    fused_image = processor.fuse_multispectral()
    
    # Procesamiento distribuido
    print("Realizando procesamiento distribuido...")
    distributed_result = processor.process_distributed()
    
    # Visualización
    print("Generando visualización...")
    plt.figure(figsize=(15, 10))
    
    # Imagen original (banda roja)
    plt.subplot(221)
    plt.imshow(image_data[0], cmap='gray')
    plt.title('Banda Roja Original')
    
    # Corrección atmosférica
    plt.subplot(222)
    plt.imshow(atmospheric_corrected[0], cmap='gray')
    plt.title('Corrección Atmosférica')
    
    # Imagen fusionada
    plt.subplot(223)
    plt.imshow(fused_image, cmap='gray')
    plt.title('Imagen Fusionada (PCA)')
    
    # Procesamiento distribuido
    plt.subplot(224)
    plt.imshow(distributed_result[0], cmap='gray')
    plt.title('Procesamiento Distribuido')
    
    plt.tight_layout()
    plt.savefig('resultados_procesamiento.png')
    print("Resultados guardados en 'resultados_procesamiento.png'")

if __name__ == "__main__":
    main() 