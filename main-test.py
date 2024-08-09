import unittest

from main import load_emission_factors, calculate_emissions


class TestCarbonFootprintCalculator(unittest.TestCase):

    def test_load_emission_factors(self):
        factors = load_emission_factors()
        self.assertIsInstance(factors, dict)
        self.assertIn('energy_sources', factors)
        self.assertIn('raw_materials', factors)
        self.assertIn('intermediate_products', factors)

    def test_calculate_emissions(self):
        emission_factors = {
            'energy_sources': {'electricity': 0.5, 'natural_gas': 2.75},
            'raw_materials': {'aluminium': 8.0, 'steel': 1.9},
            'intermediate_products': {'steel_sheets': 0.9, 'aluminium_foil': 0.5}
        }
        usage = {
            'energy_sources': {'electricity': 100, 'natural_gas': 50},
            'raw_materials': {'aluminium': 20, 'steel': 30},
            'intermediate_products': {'steel_sheets': 50, 'aluminium_foil': 10}
        }
        results = calculate_emissions(usage, emission_factors)
        self.assertAlmostEqual(results['total'], 404.5, places=1)


# 运行测试
if __name__ == '__main__':
    unittest.main()