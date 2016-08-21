from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
import operator
from srs import settings
from utilities import loadUsefulTrainingData, loadScraperDataFromDB, Sentence
import json
import os
import re
import copy

def eval_f_vec(sentence,wordlist_dict):
    """
    sentence: a single labelled sentence obj 
    returns a vector of length len(wordlist_dict)
    """
    token_list = [] #word list of the sentence
    if sentence.tokens != []:
        token_list = sentence.tokens
    else:
        # process sentence to a list of word without punctuation and number
        sentence_string = sentence.content.replace("-", " ")
        sentence_string = sentence_string.replace("/", " ")
        token_list = word_tokenize(sentence_string)
        punctuation = re.compile(r'[-.?!,":;()|0-9]') # remove these punctuations and number 
        token_list = [punctuation.sub("", word) for word in token_list]  
        token_list = filter(None, token_list) #filters empty 
        #no stemming currently, but can be easily added
        sentence.tokens = token_list

    len_word = max(len(token_list),1)*1.0;
    f_vec = copy.deepcopy(wordlist_dict) #speed up by putting copy and reset outside
    #reset to zero 
    for key in f_vec.keys():
    	for i in range(len(f_vec[key])):
    		f_vec[key][i][1]=0

    # static_aspect_list = sorted(wordlist_dict.keys())
    for key in wordlist_dict.keys():
        for i in range(len(wordlist_dict[key])):
            count = token_list.count(wordlist_dict[key][i][0])
            f_vec[key][i][1]=(count/len_word)
    
    #returns a dictionary with frequency 
    return f_vec

def cond_prob(f_vec,wordlist_dict):
	'''
	only the numerator since we only need it for prediction
	'''
	score_dict = dict.fromkeys(f_vec, 0)
	for key in f_vec.keys():
		dot_product = 0.0
		for i in range(len(wordlist_dict[key])):
			dot_product += np.exp(wordlist_dict[key][i][1]*f_vec[key][i][1])

		score_dict[key] = dot_product/len(wordlist_dict[key]) # min score is 1

	print score_dict
	return score_dict

def sentence_prediction(sentence,wordlist_dict,thres):
	'''
	predict aspect based on the score_dict. The default is the maximum
	'''
	f_vec = eval_f_vec(sentence,wordlist_dict)
	score_dict = cond_prob(f_vec,wordlist_dict)
	# print f_vec
	predicted_aspect = max(score_dict.iteritems(), key=operator.itemgetter(1))[0]
	if score_dict[predicted_aspect] == 1:
		#call word2vec similarity 
		predicted_aspect = 'no feature'

	sentence.static_aspect = predicted_aspect


if __name__ == '__main__':
	static_traning_data_dir = settings["static_training_data"]

	# sentences = loadTrainingData(static_traning_data_dir)
	sentences = loadUsefulTrainingData(static_traning_data_dir)

	# load wordlist dictionary from Tailin
	wordlist_dict_path = os.path.join(settings["predictor_data"], 'wordlist_dict_camera_wt.txt')
	wordlist_dict = json.load(open(wordlist_dict_path, 'r'))

	sentence = sentences[20]
	print sentence.content
	sentence_prediction(sentence,wordlist_dict,1)
	print sentence.static_aspect
	print sentence.labeled_aspects





