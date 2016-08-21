import unittest
from scraper import main as api_scraper, scrape_num_review_and_category
from srs_local import *
from srs import settings
from sentiment_plot import box_plot

class TestSrsLocal(unittest.TestCase):

	def test_get_right_scraped_category(self):

		product_id = 'B00V49LL90' # Samsung Galaxy Tab A 8-Inch Tablet

		_, scraped_category = scrape_num_review_and_category(product_id)

		expected_scraped_category = ['Electronics', 'Computers & Accessories', 'Computers & Tablets', 'Tablets']

		self.assertEqual(scraped_category, expected_scraped_category)

	def test_simplify_string(self):

		string = "Computers & Accessories"
		sim_string = simplify_string(string)
		expected_sim_string = "computers&accessories"

		self.assertEqual(sim_string, expected_sim_string)

	def test_get_closest_registered_category(self):

		scraped_category = ["Electronics", "Computers & Accessories", "Computers & Tablets", "Tablets"] # Samsung Galaxy Tab A 8-Inch Tablet
		registered_categories = [
			["Electronics", "Computers & Accessories", "Tablets"],
			["Electronics", "Camera & Photo", "Digital Cameras"]
		]

		closest_registered_category = get_closest_registered_category(scraped_category, registered_categories)
		expected_closest_registered_category = ["Electronics", "Computers & Accessories", "Tablets"]

		self.assertEqual(closest_registered_category, expected_closest_registered_category)

		scraped_category = ["Electronics", "Tablets"]
		registered_categories = [
			["Electronics", "Computers & Accessories", "Tablets"],
			["Electronics", "Camera & Photo", "Digital Cameras"]
		]

		closest_registered_category = get_closest_registered_category(scraped_category, registered_categories)
		expected_closest_registered_category = ["Electronics", "Computers & Accessories", "Tablets"]

		self.assertEqual(closest_registered_category, expected_closest_registered_category)

	def test_get_reviews_num_and_registered_category(self):

		product_id = 'B00V49LL90'
		_, registered_category = get_reviews_num_and_registered_category(product_id)
		expected_registered_category = ["Electronics", "Computers & Accessories","Tablets"]

		self.assertEqual(registered_category, expected_registered_category)

	def test_functionalTests(self):

		# A searches a product id to 
		# finds out srs first scrapes reviews for him
		product_id = 'B015WCV70W'
		product_name, prod_contents, prod_review_ids, prod_ratings, review_ending_sentence, scraped_pages_new = \
		api_scraper(product_id, [], [], scrape_time_limit=30)

		self.assertTrue(len(prod_contents) > 0)
		
		# the srs helps to find out what registered category
		# this product belongs to
		_, registered_category = get_reviews_num_and_registered_category(product_id)
		expected_registered_category = [ "Electronics", "Computers & Accessories", "Monitors" ]

		self.assertEqual(registered_category, expected_registered_category)

		# A thought it would be nice to use word2vec to make a review summary
		predictor_kernel = "Hybrid"
		predictor = loadTrainedPredictor(predictor_kernel, registered_category)
		prod_ft_score_dict, prod_ft_senIdx_dict = get_ft_dicts_from_contents(prod_contents, predictor)
		plot_folder = settings['sentiment_plot']
		figure_file_path = os.path.join(plot_folder, product_id + '_boxplot.png')
		box_plot(prod_ft_score_dict, figure_file_path, product_id)

		self.assertTrue(os.path.exists(figure_file_path))

if __name__ == '__main__':
	unittest.main()