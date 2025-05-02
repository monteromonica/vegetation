"""
Pruebas unitarias para el análisis de vegetación
"""

import unittest
import numpy as np
from src.vegetation_analysis import VegetationAnalyzer

class TestVegetationAnalysis(unittest.TestCase):
    def setUp(self):
        # Crear datos de prueba
        self.test_data = np.array([
            [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],  # Banda 1
            [[0.2, 0.3, 0.4], [0.5, 0.6, 0.7]],  # Banda 2
            [[0.3, 0.4, 0.5], [0.6, 0.7, 0.8]]   # Banda 3
        ])
        self.analyzer = VegetationAnalyzer(None)
        self.analyzer.image_data = self.test_data

    def test_calculate_ndvi(self):
        """Prueba el cálculo del NDVI"""
        ndvi = self.analyzer.calculate_ndvi()
        self.assertEqual(ndvi.shape, (2, 3))
        self.assertTrue(np.all(ndvi >= -1) and np.all(ndvi <= 1))

    def test_calculate_ndwi(self):
        """Prueba el cálculo del NDWI"""
        ndwi = self.analyzer.calculate_ndwi()
        self.assertEqual(ndwi.shape, (2, 3))
        self.assertTrue(np.all(ndwi >= -1) and np.all(ndwi <= 1))

    def test_calculate_evi(self):
        """Prueba el cálculo del EVI"""
        evi = self.analyzer.calculate_evi()
        self.assertEqual(evi.shape, (2, 3))
        self.assertTrue(np.all(evi >= -1) and np.all(evi <= 1))

    def test_classify_vegetation(self):
        """Prueba la clasificación de vegetación"""
        classification = self.analyzer.classify_vegetation()
        self.assertEqual(classification.shape, (2, 3))
        self.assertTrue(np.all(classification >= 0) and np.all(classification <= 3))

if __name__ == '__main__':
    unittest.main() 