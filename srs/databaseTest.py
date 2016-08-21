import unittest
from database import *

class TestCategoryCollection(unittest.TestCase):

	def test_get_all_unique_registered_categories(self):

		registered_categories = get_all_unique_registered_categories()
		registered_categories = sorted(registered_categories)
		expected_registed_categories = [
			["Cell Phones & Accessories", "Cell Phones", "No-Contract Cell Phones"],
			["Electronics", "Camera & Photo", "Digital Cameras"],
		]

		self.assertEqual(registered_categories, expected_registed_categories)