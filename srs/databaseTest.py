import unittest
from database import *

class TestCategoryCollection(unittest.TestCase):

	def test_get_all_unique_registered_categories(self):

		registered_categories = get_all_unique_registered_categories()
		registered_categories = sorted(registered_categories)
		expected_registed_categories = [
			["Electronics", "Camera & Photo", "Digital Cameras"],
			["Electronics", "Computers & Accessories", "Tablets"]
		]

		self.assertEqual(registered_categories, expected_registed_categories)