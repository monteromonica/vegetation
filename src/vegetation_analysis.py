import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from sklearn.cluster import KMeans
from datetime import datetime

class VegetationAnalyzer:
    def __init__(self, image_path):
        self.image_path = "data/" + image_path
        self.dataset = None
        self.image_data = None
        self.ndvi = None
        self.ndwi = None
        self.evi = None
        self.vegetation_classes = None
        
    def load_image(self):
        """Carga la imagen satelital usando rasterio"""
        self.dataset = rasterio.open(self.image_path)
        self.image_data = self.dataset.read()
        return self.image_data
        
    def calculate_ndvi(self):
        """
        Calcula el NDVI usando las bandas NIR (B08) y Roja (B04)
        NDVI = (NIR - RED) / (NIR + RED)
        Valores entre -1 y 1:
        - < 0: Agua, nubes, nieve
        - 0-0.1: Rocas, suelo desnudo, edificios
        - 0.1-0.3: Vegetación escasa
        - 0.3-0.6: Vegetación moderada
        - > 0.6: Vegetación densa y saludable
        """
        if self.image_data is None:
            self.load_image()
            
        # B08 (NIR) está en el índice 3, B04 (RED) en el índice 0
        nir_band = self.image_data[3].astype(float)
        red_band = self.image_data[0].astype(float)
        
        # Evitar división por cero
        denominator = nir_band + red_band
        denominator[denominator == 0] = 1
        
        self.ndvi = (nir_band - red_band) / denominator
        return self.ndvi

    def calculate_ndwi(self):
        """
        Calcula el NDWI (Índice de Agua de Diferencia Normalizada)
        NDWI = (GREEN - NIR) / (GREEN + NIR)
        """
        if self.image_data is None:
            self.load_image()
            
        # B03 (GREEN) está en el índice 1, B08 (NIR) en el índice 3
        green_band = self.image_data[1].astype(float)
        nir_band = self.image_data[3].astype(float)
        
        # Evitar división por cero
        denominator = green_band + nir_band
        denominator[denominator == 0] = 1
        
        self.ndwi = (green_band - nir_band) / denominator
        return self.ndwi

    def calculate_evi(self):
        """
        Calcula el EVI (Índice de Vegetación Mejorado)
        EVI = 2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1)
        """
        if self.image_data is None:
            self.load_image()
            
        # B08 (NIR) está en el índice 3, B04 (RED) en el índice 0, B02 (BLUE) en el índice 2
        nir_band = self.image_data[3].astype(float)
        red_band = self.image_data[0].astype(float)
        blue_band = self.image_data[2].astype(float)
        
        # Evitar división por cero
        denominator = nir_band + 6*red_band - 7.5*blue_band + 1
        denominator[denominator == 0] = 1
        
        self.evi = 2.5 * (nir_band - red_band) / denominator
        return self.evi
        
    def classify_vegetation(self, n_classes=5):
        """
        Clasifica la vegetación en n_classes categorías usando K-means
        """
        if self.ndvi is None:
            self.calculate_ndvi()
            
        # Preparar datos para clustering
        X = self.ndvi.reshape(-1, 1)
        
        # Aplicar K-means
        kmeans = KMeans(n_clusters=n_classes, random_state=42)
        self.vegetation_classes = kmeans.fit_predict(X)
        self.vegetation_classes = self.vegetation_classes.reshape(self.ndvi.shape)
        
        # Ordenar las clases por valor medio de NDVI
        class_means = []
        for i in range(n_classes):
            mask = self.vegetation_classes == i
            class_means.append((i, np.mean(self.ndvi[mask])))
        
        # Reordenar clases de menor a mayor NDVI
        class_order = [x[0] for x in sorted(class_means, key=lambda x: x[1])]
        class_map = {old: new for new, old in enumerate(class_order)}
        self.vegetation_classes = np.vectorize(class_map.get)(self.vegetation_classes)
        
        return self.vegetation_classes
        
    def analyze_vegetation_stats(self):
        """
        Calcula estadísticas básicas de vegetación
        """
        if self.ndvi is None:
            self.calculate_ndvi()
            
        stats = {
            'min_ndvi': np.min(self.ndvi),
            'max_ndvi': np.max(self.ndvi),
            'mean_ndvi': np.mean(self.ndvi),
            'std_ndvi': np.std(self.ndvi),
            'vegetation_coverage': np.sum(self.ndvi > 0.2) / self.ndvi.size * 100
        }
        
        # Calcular porcentaje por tipo de cobertura
        stats['water_snow_pct'] = np.sum(self.ndvi < 0) / self.ndvi.size * 100
        stats['bare_soil_pct'] = np.sum((self.ndvi >= 0) & (self.ndvi < 0.2)) / self.ndvi.size * 100
        stats['sparse_veg_pct'] = np.sum((self.ndvi >= 0.2) & (self.ndvi < 0.4)) / self.ndvi.size * 100
        stats['moderate_veg_pct'] = np.sum((self.ndvi >= 0.4) & (self.ndvi < 0.6)) / self.ndvi.size * 100
        stats['dense_veg_pct'] = np.sum(self.ndvi >= 0.6) / self.ndvi.size * 100
        
        # Añadir estadísticas de NDWI si está disponible
        if self.ndwi is not None:
            stats['water_bodies_pct'] = np.sum(self.ndwi > 0.2) / self.ndwi.size * 100
            
        # Añadir estadísticas de EVI si está disponible
        if self.evi is not None:
            stats['mean_evi'] = np.mean(self.evi)
            stats['max_evi'] = np.max(self.evi)
        
        return stats

    def visualize_results(self, output_path='data/vegetation_analysis.png'):
        """
        Genera visualizaciones de los resultados
        """
        if self.ndvi is None:
            self.calculate_ndvi()
            
        if self.vegetation_classes is None:
            self.classify_vegetation()
            
        # Crear un mapa de colores personalizado para NDVI
        colors = ['darkblue', 'gray', 'yellow', 'yellowgreen', 'darkgreen']
        n_bins = 256
        cmap_ndvi = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
        
        # Configurar la visualización
        plt.figure(figsize=(20, 15))
        
        # NDVI
        plt.subplot(221)
        ndvi_plot = plt.imshow(self.ndvi, cmap=cmap_ndvi, vmin=-1, vmax=1)
        plt.colorbar(ndvi_plot, label='NDVI')
        plt.title('Índice de Vegetación (NDVI)')
        
        # Clasificación
        plt.subplot(222)
        class_plot = plt.imshow(self.vegetation_classes, cmap='RdYlGn')
        plt.colorbar(class_plot, label='Clase de Vegetación')
        plt.title('Clasificación de Vegetación')
        
        # NDWI si está disponible
        if self.ndwi is not None:
            plt.subplot(223)
            ndwi_plot = plt.imshow(self.ndwi, cmap='Blues', vmin=-1, vmax=1)
            plt.colorbar(ndwi_plot, label='NDWI')
            plt.title('Índice de Agua (NDWI)')
        
        # EVI si está disponible
        if self.evi is not None:
            plt.subplot(224)
            evi_plot = plt.imshow(self.evi, cmap='YlGn', vmin=0, vmax=1)
            plt.colorbar(evi_plot, label='EVI')
            plt.title('Índice de Vegetación Mejorado (EVI)')
        
        # Guardar figura
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generar reporte de estadísticas
        stats = self.analyze_vegetation_stats()
        
        # Crear un DataFrame con las estadísticas
        stats_df = pd.DataFrame([stats])
        stats_df.to_csv('data/vegetation_stats.csv', index=False)
        
        return stats

def main():
    # Inicializar el analizador
    analyzer = VegetationAnalyzer('madrid_sentinel.tif')
    
    # Calcular índices
    print("Calculando índices de vegetación...")
    ndvi = analyzer.calculate_ndvi()
    ndwi = analyzer.calculate_ndwi()
    evi = analyzer.calculate_evi()
    
    # Clasificar vegetación
    print("Clasificando tipos de vegetación...")
    classes = analyzer.classify_vegetation()
    
    # Analizar estadísticas
    print("Analizando estadísticas...")
    stats = analyzer.analyze_vegetation_stats()
    
    # Visualizar resultados
    print("Generando visualizaciones...")
    analyzer.visualize_results()
    
    # Imprimir estadísticas principales
    print("\nEstadísticas de vegetación:")
    print(f"Cobertura vegetal total: {stats['vegetation_coverage']:.2f}%")
    print(f"Distribución de coberturas:")
    print(f"- Agua/Nieve: {stats['water_snow_pct']:.2f}%")
    print(f"- Suelo desnudo/Edificios: {stats['bare_soil_pct']:.2f}%")
    print(f"- Vegetación escasa: {stats['sparse_veg_pct']:.2f}%")
    print(f"- Vegetación moderada: {stats['moderate_veg_pct']:.2f}%")
    print(f"- Vegetación densa: {stats['dense_veg_pct']:.2f}%")
    
    if 'water_bodies_pct' in stats:
        print(f"\nCobertura de cuerpos de agua: {stats['water_bodies_pct']:.2f}%")
    
    if 'mean_evi' in stats:
        print(f"\nÍndice EVI medio: {stats['mean_evi']:.2f}")
        print(f"Índice EVI máximo: {stats['max_evi']:.2f}")
    
    print("\nResultados guardados en 'vegetation_analysis.png' y 'vegetation_stats.csv'")

if __name__ == "__main__":
    main() 