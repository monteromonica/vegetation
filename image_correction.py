import numpy as np
import rasterio
import cv2
from scipy import ndimage
from skimage import restoration, exposure
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from rasterio.warp import calculate_default_transform, reproject, Resampling

class ImageCorrector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.dataset = None
        self.image_data = None
        self.corrected_data = None
        
    def load_image(self):
        """Carga la imagen satelital"""
        self.dataset = rasterio.open(self.image_path)
        self.image_data = self.dataset.read()
        return self.image_data

    def apply_noise_reduction(self, method='gaussian', **kwargs):
        """
        Aplica reducción de ruido usando diferentes métodos
        
        Métodos disponibles:
        - 'gaussian': Filtro gaussiano
        - 'median': Filtro de mediana
        - 'bilateral': Filtro bilateral (preserva bordes)
        - 'nlm': Non-Local Means denoising
        """
        if self.image_data is None:
            self.load_image()
            
        self.corrected_data = np.zeros_like(self.image_data)
        
        for band in range(self.image_data.shape[0]):
            band_data = self.image_data[band]
            
            if method == 'gaussian':
                sigma = kwargs.get('sigma', 1)
                filtered = gaussian_filter(band_data, sigma=sigma)
            
            elif method == 'median':
                size = kwargs.get('size', 3)
                filtered = ndimage.median_filter(band_data, size=size)
            
            elif method == 'bilateral':
                d = kwargs.get('d', 9)
                sigmaColor = kwargs.get('sigmaColor', 75)
                sigmaSpace = kwargs.get('sigmaSpace', 75)
                filtered = cv2.bilateralFilter(band_data.astype(np.uint8), d, sigmaColor, sigmaSpace)
            
            elif method == 'nlm':
                filtered = restoration.denoise_nl_means(band_data, 
                                                      patch_size=kwargs.get('patch_size', 5),
                                                      patch_distance=kwargs.get('patch_distance', 6))
                filtered = (filtered * 255).astype(np.uint8)
            
            self.corrected_data[band] = filtered
            
        return self.corrected_data

    def apply_atmospheric_correction(self, method='dos'):
        """
        Aplica corrección atmosférica
        
        Métodos:
        - 'dos': Dark Object Subtraction
        - 'histogram': Equalización de histograma
        """
        if self.image_data is None:
            self.load_image()
            
        self.corrected_data = np.zeros_like(self.image_data, dtype=float)
        
        for band in range(self.image_data.shape[0]):
            band_data = self.image_data[band].astype(float)
            
            if method == 'dos':
                # Asume que el valor más oscuro representa dispersión atmosférica
                dark_value = np.percentile(band_data, 1)
                corrected = band_data - dark_value
                corrected[corrected < 0] = 0
                
            elif method == 'histogram':
                corrected = exposure.equalize_hist(band_data)
                corrected = (corrected * 255).astype(np.uint8)
                
            self.corrected_data[band] = corrected
            
        return self.corrected_data

    def apply_radiometric_correction(self):
        """
        Aplica corrección radiométrica básica:
        - Normalización de valores
        - Corrección de saturación
        - Ajuste de contraste
        """
        if self.image_data is None:
            self.load_image()
            
        self.corrected_data = np.zeros_like(self.image_data, dtype=float)
        
        for band in range(self.image_data.shape[0]):
            band_data = self.image_data[band].astype(float)
            
            # Normalización min-max
            normalized = (band_data - band_data.min()) / (band_data.max() - band_data.min())
            
            # Ajuste de contraste
            p2, p98 = np.percentile(normalized, (2, 98))
            corrected = exposure.rescale_intensity(normalized, in_range=(p2, p98))
            
            # Convertir a uint8
            self.corrected_data[band] = (corrected * 255).astype(np.uint8)
            
        return self.corrected_data

    def apply_geometric_correction(self, dst_crs='EPSG:4326'):
        """
        Aplica corrección geométrica básica:
        - Reproyección a un CRS específico
        - Corrección de distorsión
        """
        if self.image_data is None:
            self.load_image()
            
        # Calcular transformación
        transform, width, height = calculate_default_transform(
            self.dataset.crs, dst_crs, 
            self.dataset.width, self.dataset.height, 
            *self.dataset.bounds)
            
        # Inicializar array para datos corregidos
        self.corrected_data = np.zeros((self.dataset.count, height, width))
        
        # Reproyectar cada banda
        for band in range(self.dataset.count):
            reproject(
                source=self.image_data[band],
                destination=self.corrected_data[band],
                src_transform=self.dataset.transform,
                src_crs=self.dataset.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.bilinear)
                
        return self.corrected_data

    def visualize_corrections(self, band_index=0):
        """
        Visualiza los resultados de las correcciones para una banda específica
        """
        if self.image_data is None:
            self.load_image()
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 15))
        
        # Imagen original
        print("Visualizando imagen original...")
        axes[0,0].imshow(self.image_data[band_index], cmap='gray')
        axes[0,0].set_title('Imagen Original')
        
        # Reducción de ruido
        print("Aplicando reducción de ruido...")
        noise_reduced = self.apply_noise_reduction(method='bilateral')
        axes[0,1].imshow(noise_reduced[band_index], cmap='gray')
        axes[0,1].set_title('Reducción de Ruido (Bilateral)')
        
        # Corrección atmosférica
        print("Aplicando corrección atmosférica...")
        atm_corrected = self.apply_atmospheric_correction(method='dos')
        axes[1,0].imshow(atm_corrected[band_index], cmap='gray')
        axes[1,0].set_title('Corrección Atmosférica (DOS)')
        
        # Corrección radiométrica
        print("Aplicando corrección radiométrica...")
        rad_corrected = self.apply_radiometric_correction()
        axes[1,1].imshow(rad_corrected[band_index], cmap='gray')
        axes[1,1].set_title('Corrección Radiométrica')
        
        plt.tight_layout()
        plt.savefig('correction_results.png')
        plt.close()

def main():
    # Inicializar el corrector
    corrector = ImageCorrector('madrid_sentinel.tif')
    
    # Cargar imagen
    print("Cargando imagen...")
    corrector.load_image()
    
    # Visualizar todas las correcciones
    print("Aplicando y visualizando correcciones...")
    corrector.visualize_corrections()
    
    print("\nResultados guardados en 'correction_results.png'")
    
if __name__ == "__main__":
    main() 