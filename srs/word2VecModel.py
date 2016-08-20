import numpy as np
import math as math
import word2vec
from utilities import Sentence, Product, AspectPattern

class AspectPatterns(object):
	def __init__(self, pattern_name_list):
		#possible pattern_name: adj_nn, nn, adj, adv
		self.aspectPatterns_list = []
		for pattern_name in pattern_name_list:
			if pattern_name == 'adj_nn':
				aspectPatterns_1 = []
				pattern_structure ="""adj_nn:{<JJ><NN.?>}"""
				aspectTagIndices = [0,1]
				aspectPattern = AspectPattern(name='adj_nn', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_1.append(aspectPattern)

				pattern_structure ="""nn_nn:{<NN.?><NN.?>}"""
				aspectPattern = AspectPattern(name='nn_nn', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_1.append(aspectPattern)
				self.aspectPatterns_list.append(aspectPatterns_1)

			elif pattern_name == 'nn':
				aspectPatterns_2 = []
				pattern_structure ="""nn:{<NN.?>}"""
				aspectTagIndices = [0]
				aspectPattern = AspectPattern(name='nn', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_2.append(aspectPattern)
				self.aspectPatterns_list.append(aspectPatterns_2)

			elif pattern_name == 'adj':
				aspectPatterns_3 = []
				pattern_structure ="""adj:{<JJ.?>}"""
				aspectTagIndices = [0]
				aspectPattern = AspectPattern(name='adj', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_3.append(aspectPattern)
				self.aspectPatterns_list.append(aspectPatterns_3)

			elif pattern_name == 'adv':
				aspectPatterns_4 = []
				pattern_structure ="""adv_compara:{<RBR>}"""
				aspectTagIndices = [0]
				aspectPattern = AspectPattern(name='adv_compara', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_4.append(aspectPattern)

				pattern_structure ="""adv_super:{<RBS>}"""
				aspectTagIndices = [0]
				aspectPattern = AspectPattern(name='adv_super', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_4.append(aspectPattern)
				self.aspectPatterns_list.append(aspectPatterns_4)


def distill_dynamic(sentence, aspectPatterns):
	if not sentence.pos_tagged_tokens:
		sentence.pos_tag(stem=False)
	sentence.word2vec_matchDaynamicAspectPatterns(aspectPatterns.aspectPatterns_list)

def distill_dynamic_sentencelist(sentence_list, aspectPatterns):
	for sentence in sentence_list:
		distill_dynamic(sentence, aspectPatterns)


def static_aspect_to_vec(wordlist_dict, model):

	static_seedwords_vec={}
	for static_aspect, seedwords in wordlist_dict.iteritems(): 
		for word in seedwords:
			if word in model:
				if static_aspect in static_seedwords_vec:
					static_seedwords_vec[static_aspect].append(model[word])
				else:
					static_seedwords_vec[static_aspect] = [model[word]]

	return static_seedwords_vec

def getPhraseWordVectorsList(sentence, aspectPatterns, word2vecModel):

	# match aspect patterns
	distill_dynamic(sentence, aspectPatterns)

	phrases = []
	for item in sentence.word2vec_features_list:
		phrases = phrases + item
	
	phrasewordVecs_list=[]
	for phrase in phrases:
		phraseWords = phrase.split(' ')
		phraseWordVecs=[]
		for phraseWord in phraseWords:
			if phraseWord in word2vecModel:
				phrasewordVec = word2vecModel[phraseWord]
				phraseWordVecs.append(phrasewordVec)
		if phraseWordVecs:
			phrasewordVecs_list.append(phraseWordVecs)

	return phrasewordVecs_list

def getPhraseAspectCosineSimilarityMatrix(phrasewordVecs_list, static_seedwords_vec, similarity_measure='max'):

	num_static_aspect = len(static_seedwords_vec)
	static_aspects = sorted(static_seedwords_vec.keys())

	num_phrase = len(phrasewordVecs_list)
	similarity_matrix=np.zeros([num_phrase, num_static_aspect]) if num_phrase>=1 else np.zeros([1, num_static_aspect])
	for i, phrasewordVecs in enumerate(phrasewordVecs_list):
			for j, static_aspect in enumerate(static_aspects):
				seedwordVecs = static_seedwords_vec[static_aspect]
				similarity_inner_matrix=np.zeros([len(phrasewordVecs),len(seedwordVecs)])
				for ii, phrasewordVec in enumerate(phrasewordVecs):
					for jj, seedwordVec in enumerate(seedwordVecs):
						similarity_inner_matrix[ii][jj]=np.dot(phrasewordVec,seedwordVec)

				if similarity_measure == 'max':
					similarity_inner_row=np.max(similarity_inner_matrix, axis=1)
					similarity_inner=np.sum(similarity_inner_row)
				elif similarity_measure == 'sum_row_max':
					similarity_inner_row=np.max(similarity_inner_matrix,axis=1)
					similarity_inner=np.sum(similarity_inner_row)
				elif similarity_measure == 'max_column_mean':
					similarity_inner_column=np.mean(similarity_inner_matrix,axis=0)
					similarity_inner=np.max(similarity_inner_column)
				elif similarity_measure == 'mean':
					similarity_inner=np.mean(similarity_inner_matrix)

				similarity_matrix[i][j]=similarity_inner

	return similarity_matrix

def getSimilarityVectorFromSimilarityMatrix(similarity_matrix, criteria='max'):

	num_static_aspect = similarity_matrix.shape[1]
	similarity_vec=[0 for j in range(num_static_aspect)]
	if criteria == 'max':
		for j in range(num_static_aspect):
			similarity_vec[j]=np.max(similarity_matrix[:,j])
	elif criteria == 'sum':
		for j in range(num_static_aspect):
			similarity_vec[j]=np.sum(similarity_matrix[:,j])
	elif criteria == 'sum_max':
		similarity_maxmatching_matrix=np.zeros([len(phrasewordVecs_list),num_static_aspect])
		for i in range(len(phrasewordVecs_list)):
			k=0
			max_k=0
			for j in range(num_static_aspect):
				if similarity_matrix[i,j]>max_k:
					k=j
					max_k=similarity_matrix[i,j]
			similarity_maxmatching_matrix[i,k]=max_k
		for j in range(num_static_aspect):
			similarity_vec[j]=np.sum(similarity_maxmatching_matrix[:,j])

	return np.array(similarity_vec)


def getCosineSimilarityVector(sentence, aspectPatterns, word2vecModel, static_seedwords_vec):
	
	phrasewordVecs_list = getPhraseWordVectorsList(sentence, aspectPatterns, word2vecModel)

	if phrasewordVecs_list:
		similarity_matrix = getPhraseAspectCosineSimilarityMatrix(phrasewordVecs_list, static_seedwords_vec)
		similarity_vec = getSimilarityVectorFromSimilarityMatrix(similarity_matrix, criteria='max')
	else:
		similarity_vec = np.zeros(len(static_seedwords_vec))

	return similarity_vec

def predict_aspect_word2vec(sentence, word2vecModel, aspectPatterns, static_seedwords_vec, cp_threshold = 0.85, ratio_threshold = 0):
	# aspectPattern_namelist: 'adj_nn': all adj+nn and nn+nn; 'nn': all nn; adj: all adj; adv: all adv
	# cp_threshold: the threshold for the top class's similarity, for a sentence to be classified as useful
	# ratio_threshold: the threshold for the ratio between top and second class's similarity, for a sentence to be classified as useful

	phrasewordVecs_list = getPhraseWordVectorsList(sentence, aspectPatterns, word2vecModel)	
	
	if phrasewordVecs_list:
		similarity_matrix = getPhraseAspectCosineSimilarityMatrix(phrasewordVecs_list, static_seedwords_vec)

		similarity_vec = getSimilarityVectorFromSimilarityMatrix(similarity_matrix)

		# Sort the sentence's similarity to each class
		static_aspects = sorted(static_seedwords_vec.keys())
		aspect_similarity_tups_sorted = sorted(zip(static_aspects, similarity_vec), 
			key=lambda tup: tup[1], reverse=True)
		if aspect_similarity_tups_sorted[0][1]>cp_threshold:
			if aspect_similarity_tups_sorted[1][1]!=0 and aspect_similarity_tups_sorted[0][1]/aspect_similarity_tups_sorted[1][1]>=ratio_threshold:
				prediction=aspect_similarity_tups_sorted[0][0]
			elif aspect_similarity_tups_sorted[1][1]==0 and aspect_similarity_tups_sorted[0][1]!=0:
				prediction=aspect_similarity_tups_sorted[0][0]
			else: prediction='no feature'
		else: prediction='no feature'
		return (prediction,aspect_similarity_tups_sorted)
	else:
		return ('no feature',[])