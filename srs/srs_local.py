from scraper import main as api_scraper, scrape_num_review_and_category
from predictor import MaxEntropy_Predictor, Word2Vec_Predictor, loadTrainedPredictor
from srs import settings
from utilities import loadScraperDataFromDB, Sentence
from vanderModel import get_sentiment_score_for_sentences, get_ftScore_ftSenIdx_dicts
from sentiment_plot import box_plot
from database import (upsert_contents_for_product_id, 
update_score_for_product_id, update_num_reviews_for_product_id, 
update_contents_for_product_id, select_for_product_id, get_all_unique_registered_categories)
import os

def get_ft_dicts_from_contents(contents, predictor, start_idx = 0):
	sentences = []
	for cont in contents:
		sentences.append(Sentence(content=cont))
	
	predictor.predict_for_sentences(sentences)	#if Maxentropy, the cp_threshold=0.5, if Word2Vec, the cp_threshold should be 0.85 for criteria_for_choosing_class = "max", similarity_measure = "max"
	get_sentiment_score_for_sentences(sentences)
	return get_ftScore_ftSenIdx_dicts(sentences, start_idx)
	
def get_closest_registered_category(scraped_category, registered_categories):

	sim_scraped_category = [simplify_string(category_layer) for category_layer in scraped_category]

	registeredCategory_matchedLayer_dict = {}
	for registered_category in registered_categories:
		sim_registered_category = [simplify_string(category_layer) for category_layer in registered_category]
		matched_layers = []
		for layer in sim_scraped_category:
			if layer in sim_registered_category:
				matched_layers.append(1)
			else:
				matched_layers.append(0)
		registeredCategory_matchedLayer_dict[tuple(registered_category)] = matched_layers

	sorted_registeredCategory_matchedLayer_list = sorted(registeredCategory_matchedLayer_dict.items(),
		key=lambda item: item[1], reverse=True)

	best_matched_layer = sorted_registeredCategory_matchedLayer_list[0][1]

	# if best matched category still not matching first two levels of scraped_category
	# let user know srs is not ready for that
	if best_matched_layer[0] < 1 or best_matched_layer[0] < 1:
		return []
	else:
		return list(sorted_registeredCategory_matchedLayer_list[0][0])

def get_reviews_num_and_registered_category(product_id):
	"""
	Return a hirarchical category registered in the srs databse to which
	product belongs. The hirarchical category is mostly same as scraped category 
	from amazon, but the scraped category can change at amazon's will.
	This return registered category is associated with wordlist, which will be further 
	fed to predictor for sentence aspect classification. 
	"""
	num_reviews, scraped_category = scrape_num_review_and_category(product_id)

	registered_categories = get_all_unique_registered_categories()

	return num_reviews, get_closest_registered_category(scraped_category, registered_categories)


def simplify_string(string):

	return string.lower().replace(" ", "")

def fill_in_db(product_id, predictor_kernel='Hybrid', review_ratio_threshold = 0.8, scrape_time_limit = 30):	
	# fetch product info from db
	query_res = select_for_product_id(product_id)

	if len(query_res) == 0: # not in db yet
		print "{0} NOT exists in db, now scraping reviews...".format(product_id)
		# scrape product info and review contents:
		product_name, prod_contents, prod_review_ids, prod_ratings, review_ending_sentence, scraped_pages_new = api_scraper(product_id, [], [], scrape_time_limit)
		
		if len(prod_contents) <= 0:
			print "Do not find reviews for %s" % product_id
			return False
		else:
			prod_num_reviews, registered_category = get_reviews_num_and_registered_category(product_id)	
			if prod_num_reviews == -1:
				prod_num_reviews = len(prod_review_ids)

			# classify, sentiment score
			predictor = loadTrainedPredictor(predictor_kernel, registered_category)
			prod_ft_score_dict, prod_ft_senIdx_dict = get_ft_dicts_from_contents(prod_contents, predictor)
		
			# insert new entry
			upsert_contents_for_product_id(product_id, product_name, prod_contents, prod_review_ids,\
			 prod_ratings, review_ending_sentence, scraped_pages_new, prod_num_reviews, registered_category, \
				prod_ft_score_dict, prod_ft_senIdx_dict)
			return True	

	else:

		print "{0} ALREADY in db".format(product_id)
		# extract previous data in db:
		prod_contents = query_res[0]["contents"]
		prod_ft_score_dict = query_res[0]["ft_score"]
		prod_ft_senIdx_dict = query_res[0]["ft_senIdx"]
		prod_review_ids_db = query_res[0]["review_ids"]
		prod_scraped_pages = query_res[0]["scraped_pages"]
		prod_num_reviews_previous = query_res[0]['num_reviews']
		num_review_db = len(query_res[0]["review_ids"])

		# scrape for total number of review and category
		prod_num_reviews, registered_category = get_reviews_num_and_registered_category(product_id)	
		
		if prod_num_reviews == -1: # fail to get the real number
			prod_num_reviews = prod_num_reviews_previous
		elif prod_num_reviews > prod_num_reviews_previous:
			update_num_reviews_for_product_id(product_id, prod_num_reviews)
			print "Found more new reviews in Amazon: updating product's num_reviews field..."

		if num_review_db < review_ratio_threshold * prod_num_reviews and num_review_db < 100: 
			print "Not enough reviews in db: scrapping for more..."
			# scrape contents
			if not prod_scraped_pages:
				prod_scraped_pages = []
			_, prod_contents_new, prod_review_ids, prod_ratings, review_ending_sentence, scraped_pages_new = \
			api_scraper(product_id, prod_review_ids_db, prod_scraped_pages, scrape_time_limit)		

			# classify, get sentiment score
			if len(prod_contents_new) > 0:			
				prod_contents = prod_contents + prod_contents_new
				
				predictor = loadTrainedPredictor(predictor_kernel, registered_category)
				prod_ft_score_dict, prod_ft_senIdx_dict = get_ft_dicts_from_contents(prod_contents, predictor)
				
				# append new entry to existing entry
				update_contents_for_product_id(product_id, prod_contents_new, prod_review_ids, \
					prod_ratings, review_ending_sentence, scraped_pages_new, registered_category, \
					prod_ft_score_dict, prod_ft_senIdx_dict)
				return True

			else:
				print "No New Reviews Found: %s" % product_id
				if len(prod_ft_score_dict) == 0 or len(prod_ft_senIdx_dict) == 0:
					predictor = loadTrainedPredictor(predictor_kernel, registered_category)
					prod_ft_score_dict, prod_ft_senIdx_dict = get_ft_dicts_from_contents(prod_contents, predictor)

					update_score_for_product_id(product_id, prod_ft_score_dict, prod_ft_senIdx_dict)

				return True

		else:
			print "Got Enough Reviews in db"
			if len(prod_ft_score_dict) == 0 or len(prod_ft_senIdx_dict) == 0:
				# classify, sentiment score
				predictor = loadTrainedPredictor(predictor_kernel, registered_category)
				prod_ft_score_dict, prod_ft_senIdx_dict = \
				get_ft_dicts_from_contents(prod_contents, predictor)
				
				# update old entry
				update_score_for_product_id(product_id, prod_ft_score_dict, prod_ft_senIdx_dict)

				return True
			else:
				return True
	
	
def plot(product_id):
	_, prod1_ft_score_dict, _ = loadScraperDataFromDB(product_id)
	plot_folder = settings['sentiment_plot']
	figure_file_path = os.path.join(plot_folder, product_id + '_boxplot.png')
	box_plot(prod1_ft_score_dict, figure_file_path, product_id)

def main(product_id):
	fill_in_db(product_id)
	plot(product_id)

if __name__ == '__main__':
	product_id = 'B00V49LL90'
	product_name, prod_contents, prod_review_ids, prod_ratings, review_ending_sentence, scraped_pages_new = \
	api_scraper(product_id, [], [], scrape_time_limit=5)

	_, registered_category = get_reviews_num_and_registered_category(product_id)

	# A thought it would be nice to use word2vec to make a review summary
	predictor_kernel = "Hybrid"
	predictor = loadTrainedPredictor(predictor_kernel, registered_category)

	prod_ft_score_dict, prod_ft_senIdx_dict = get_ft_dicts_from_contents(prod_contents, predictor)
	plot_folder = settings['sentiment_plot']
	figure_file_path = os.path.join(plot_folder, product_id + '_boxplot.png')
	box_plot(prod_ft_score_dict, figure_file_path, product_id)

