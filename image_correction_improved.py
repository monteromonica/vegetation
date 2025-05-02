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
                d = kwargs.get('d', 11)  # Aumentado de 9 a 11
                sigmaColor = kwargs.get('sigmaColor', 50)  # Reducido de 75 a 50
                sigmaSpace = kwargs.get('sigmaSpace', 50)  # Reducido de 75 a 50
                filtered = cv2.bilateralFilter(band_data.astype(np.uint8), d, sigmaColor, sigmaSpace)
            
            elif method == 'nlm':
                filtered = restoration.denoise_nl_means(band_data, 
                                                      patch_size=kwargs.get('patch_size', 5),
                                                      patch_distance=kwargs.get('patch_distance', 6))
                filtered = (filtered * 255).astype(np.uint8)
            
            self.corrected_data[band] = filtered
            
        return self.corrected_data

    def apply_atmospheric_correction(self, method='dos', percentile=0.5):
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
                # Usar un percentil más bajo para la corrección atmosférica
                dark_value = np.percentile(band_data, percentile)
                corrected = band_data - dark_value
                corrected[corrected < 0] = 0
                
            elif method == 'histogram':
                corrected = exposure.equalize_hist(band_data)
                corrected = (corrected * 255).astype(np.uint8)
                
            self.corrected_data[band] = corrected
            
        return self.corrected_data

    def apply_radiometric_correction(self, p_low=1, p_high=99):
        """
        Aplica corrección radiométrica básica con percentiles ajustables
        """
        if self.image_data is None:
            self.load_image()
            
        self.corrected_data = np.zeros_like(self.image_data, dtype=float)
        
        for band in range(self.image_data.shape[0]):
            band_data = self.image_data[band].astype(float)
            
            # Normalización min-max
            normalized = (band_data - band_data.min()) / (band_data.max() - band_data.min())
            
            # Ajuste de contraste con percentiles personalizables
            p_min, p_max = np.percentile(normalized, (p_low, p_high))
            corrected = exposure.rescale_intensity(normalized, in_range=(p_min, p_max))
            
            # Convertir a uint8
            self.corrected_data[band] = (corrected * 255).astype(np.uint8)
            
        return self.corrected_data

    def visualize_corrections(self, band_index=0, compare=True):
        """
        Visualiza los resultados de las correcciones para una banda específica
        """
        if self.image_data is None:
            self.load_image()
            
        # Configurar el tamaño de la figura según si queremos comparar o no
        if compare:
            fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        else:
            fig, axes = plt.subplots(2, 2, figsize=(15, 15))
        
        # Imagen original
        print("Visualizando imagen original...")
        if compare:
            axes[0,0].imshow(self.image_data[band_index], cmap='gray')
            axes[0,0].set_title('Original (Sin ajustes)')
        else:
            axes[0,0].imshow(self.image_data[band_index], cmap='gray')
            axes[0,0].set_title('Imagen Original')
        
        # Reducción de ruido
        print("Aplicando reducción de ruido...")
        # Parámetros originales
        if compare:
            noise_reduced_orig = self.apply_noise_reduction(method='bilateral', d=9, sigmaColor=75, sigmaSpace=75)
            axes[0,1].imshow(noise_reduced_orig[band_index], cmap='gray')
            axes[0,1].set_title('Reducción Ruido (Original)')
        
        # Nuevos parámetros
        noise_reduced = self.apply_noise_reduction(method='bilateral', d=11, sigmaColor=50, sigmaSpace=50)
        if compare:
            axes[0,2].imshow(noise_reduced[band_index], cmap='gray')
            axes[0,2].set_title('Reducción Ruido (Mejorado)')
        else:
            axes[0,1].imshow(noise_reduced[band_index], cmap='gray')
            axes[0,1].set_title('Reducción de Ruido (Bilateral)')
        
        # Corrección atmosférica
        print("Aplicando corrección atmosférica...")
        # Parámetros originales
        if compare:
            atm_corrected_orig = self.apply_atmospheric_correction(method='dos', percentile=1.0)
            axes[1,1].imshow(atm_corrected_orig[band_index], cmap='gray')
            axes[1,1].set_title('Atm. Corrección (Original)')
        
        # Nuevos parámetros
        atm_corrected = self.apply_atmospheric_correction(method='dos', percentile=0.5)
        if compare:
            axes[1,2].imshow(atm_corrected[band_index], cmap='gray')
            axes[1,2].set_title('Atm. Corrección (Mejorado)')
        else:
            axes[1,0].imshow(atm_corrected[band_index], cmap='gray')
            axes[1,0].set_title('Corrección Atmosférica (DOS)')
        
        # Corrección radiométrica
        print("Aplicando corrección radiométrica...")
        # Parámetros originales
        if compare:
            rad_corrected_orig = self.apply_radiometric_correction(p_low=2, p_high=98)
            axes[0,3].imshow(rad_corrected_orig[band_index], cmap='gray')
            axes[0,3].set_title('Rad. Corrección (Original)')
        
        # Nuevos parámetros
        rad_corrected = self.apply_radiometric_correction(p_low=1, p_high=99)
        if compare:
            axes[1,3].imshow(rad_corrected[band_index], cmap='gray')
            axes[1,3].set_title('Rad. Corrección (Mejorado)')
        else:
            axes[1,1].imshow(rad_corrected[band_index], cmap='gray')
            axes[1,1].set_title('Corrección Radiométrica')
        
        plt.tight_layout()
        if compare:
            plt.savefig('correction_results_comparison.png')
        else:
            plt.savefig('correction_results.png')
        plt.close()

def main():
    # Inicializar el corrector
    corrector = ImageCorrector('madrid_sentinel.tif')
    
    # Cargar imagen
    print("Cargando imagen...")
    corrector.load_image()
    
    # Visualizar todas las correcciones con comparación
    print("Aplicando y visualizando correcciones...")
    corrector.visualize_corrections(compare=True)
    
    print("\nResultados guardados en 'correction_results_comparison.png'")
    
if __name__ == "__main__":
    main() 