import unittest
from hybridModel import *
from utilities import Sentence

class TestHybridModel(unittest.TestCase):
    # load wordlist dictionary txt from Tailin
    wordlist_dict_path = os.path.join(settings["predictor_data"], 'wordlist_dict_camera_wt.txt')
    wordlist_dict = json.load(open(wordlist_dict_path, 'r'))

    # load word2vec model
    model_filename = 'text8.bin'
    model_file_path = getPredictorDataFilePath(model_filename)
    w2v_model = word2vec.load(model_file_path)  #load word2vec model

    def test_empty_case(self):
        sentence = Sentence('')
        sentence_prediction(sentence,self.wordlist_dict,self.w2v_model,0.85)
        self.assertEqual(sentence.static_aspect,'no feature')


if __name__ == '__main__':
    unittest.main()


