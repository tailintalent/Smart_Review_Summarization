import numpy as np
import operator
from srs import settings
from utilities import tokenize, loadUsefulTrainingData, loadScraperDataFromDB, Sentence, AspectPattern
import json
import os
import re
import copy
import word2vec

def eval_f_vec(sentence,wordlist_dict):
    """
    sentence: a single labelled sentence obj 
    returns a vector of length len(wordlist_dict)
    """
    #tokenize the sentence if not already
    if not sentence.tokens:
    	# not tokenize before 
    	token_list = tokenize(sentence.content, stem=False)
    	sentence.tokens = token_list
    else:
		token_list = sentence.tokens
    len_word = max(len(token_list),1)*1.0;
    f_vec = copy.deepcopy(wordlist_dict) #speed up by putting copy and reset outside
    #reset to zero 
    for key in f_vec.keys():
    	for i in range(len(f_vec[key])):
    		f_vec[key][i][1]=0

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

def sentence_prediction(sentence,wordlist_dict,w2v_model,thres):
	'''
	predict aspect based on the score_dict. The default is the maximum
	'''
	f_vec = eval_f_vec(sentence,wordlist_dict)
	score_dict = cond_prob(f_vec,wordlist_dict)
	# print f_vec
	predicted_aspect = max(score_dict.iteritems(), key=operator.itemgetter(1))[0]
	if score_dict[predicted_aspect] == 1: # no key word overlap
		#call word2vec similarity 
		score_dict_w2v = word2vec_predict(sentence,wordlist_dict,w2v_model)
		predicted_aspect = max(score_dict_w2v.iteritems(), key=operator.itemgetter(1))[0]
		if score_dict_w2v[predicted_aspect] < thres:
			predicted_aspect = 'no feature'

	sentence.static_aspect = predicted_aspect

def word2vec_predict(sentence,wordlist_dict,w2v_model):
	s_vec = eval_s_vec(sentence,wordlist_dict,w2v_model)
	#post process to return an aspect of most similar
	score_dict_w2v = dict.fromkeys(s_vec, 0)
	# 1. get the maximum of each seed without weight (weight doesn't do well)
	for key in s_vec.keys():
		dot_product = 0.0
		similarity_wt_max = 0
		for i in range(len(wordlist_dict[key])):
			similarity_wt = s_vec[key][i][1]
			if similarity_wt > similarity_wt_max:
				similarity_wt_max = similarity_wt
		score_dict_w2v[key] = similarity_wt_max 

	print score_dict_w2v
	return score_dict_w2v

def eval_s_vec(sentence,wordlist_dict,w2v_model):
	token_list_full = sentence.tokens
	token_list = distill_token(token_list_full)
	# create cosine similarity matrix
	s_vec = copy.deepcopy(wordlist_dict) #speed up by putting copy and reset outside
	#reset to zero 
	for key in s_vec.keys():
		for i in range(len(s_vec[key])):
			s_vec[key][i][1]=0

	for key in wordlist_dict.keys():
	    for i in range(len(wordlist_dict[key])):
	    	v_seed = w2v_model[wordlist_dict[key][i][0]]
	    	similarity = []
	    	for token in token_list:
	    		if token in w2v_model:
	    			v_token = w2v_model[token]
	    			# similarity.append(np.linalg.norm(v_token-v_seed))
	    			similarity.append(np.dot(v_token,v_seed))
	    		else: 
	    			similarity.append(0)
	    	max_idx = similarity.index(max(similarity))
	    	# print (token_list[max_idx],wordlist_dict[key][i][0],similarity[max_idx])
	    	s_vec[key][i][1] = max(similarity)

	return s_vec

def distill_token(token_list):

	from nltk.corpus import stopwords
	token_list_distill = [word for word in token_list if word not in stopwords.words('english')]

	return token_list_distill

def getPredictorDataFilePath(filename):
		
	predictor_datafile_path = os.path.join(settings["predictor_data"], filename)
	if os.path.exists(predictor_datafile_path):
		return predictor_datafile_path
	else:
		raise Exception("{} is not found!".format(predictor_datafile_path))


if __name__ == '__main__':
	static_traning_data_dir = settings["static_training_data"]

	# sentences = loadTrainingData(static_traning_data_dir)
	sentences = loadUsefulTrainingData(static_traning_data_dir)

	# load wordlist dictionary from Tailin
	wordlist_dict_path = os.path.join(settings["predictor_data"], 'wordlist_dict_camera_wt.txt')
	wordlist_dict = json.load(open(wordlist_dict_path, 'r'))

	# load word2vec model
	model_filename = 'text8.bin'
	model_file_path = getPredictorDataFilePath(model_filename)
	w2v_model = word2vec.load(model_file_path)  #load word2vec model

	#begin testing
	# sentence = sentences[122] # change index for different sentences 
	sentence = Sentence('I find it easy to operate.')

	print sentence.content
	sentence_prediction(sentence,wordlist_dict,w2v_model,0.85)
	print sentence.static_aspect
	print sentence.labeled_aspects


