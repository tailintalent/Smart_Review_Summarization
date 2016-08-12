from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
from collections import defaultdict

def get_sentiment_score(ls):
	'''
	input sentence object
	this method estimate a sentiment score based on vander model
	'''
	vs = vaderSentiment(ls.content.encode('ascii', 'ignore')) # encode is important to avoid error
	# sample output of vs: {'neg': 0.736, 'neu': 0.264, 'pos': 0.0, 'compound': -0.4199}
	ls.score = vs['pos']-vs['neg']

def get_sentiment_score_for_sentences(sentences):

    for sentence in sentences:
        get_sentiment_score(sentence)

def get_ftScore_ftSenIdx_dicts(sentences, start_idx = 0, forbidden_feature='no feature'):
    '''
    sentences: a list of sentence object
    staticPredictor object
    return a list of individual score for each static feature via a dictionary
    '''
    ft_score_dict = defaultdict(list)
    ft_senIdx_dict = defaultdict(list)
    for idx, sentence in enumerate(sentences):
        ft = sentence.static_aspect
        if not ft == forbidden_feature:
            ft_score_dict[ft].append(sentence.score)
            ft_senIdx_dict[ft].append(idx + start_idx)

    return ft_score_dict, ft_senIdx_dict

