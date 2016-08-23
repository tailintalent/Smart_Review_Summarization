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

    def test_general_case(self):
        aspect=[k for k in self.wordlist_dict.keys()]
        aspect.append('no feature')

        content_list = ["I find it easy to operate.",
                        "Obviously, if you're a serious photographer, this is not the camera for you, but for me, it's great.",
                        "After several hours of use, the flickering seemed to mostly go away, but not entirely"]
        test_result = True
        for c in content_list:
            sentence = Sentence(c)
            sentence_prediction(sentence,self.wordlist_dict,self.w2v_model,0.85)
            if sentence.static_aspect not in aspect:
                test_result = False 

        self.assertTrue(test_result)

if __name__ == '__main__':
    unittest.main()


