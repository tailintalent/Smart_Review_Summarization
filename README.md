# Smart_Review_Summarization
An automatic summarization tool for product reviews

## Dependencies management

### Anaconda environment creation
If you never use anaconda before please install that before proceeding.
```
cd Smart_Review_Summarization
conda env create -f environment.yml
source activate srs
```

### other packages installation (those not available in `conda` channels)
```
pip install -r requirements.txt
```

### `nltk_data/tokenizers` and `nltk_data/corpora`
```
python
nltk.download()
```
choose `punkt` for tokenizer, `sentiwordnet` and `wordnet` for corpora.

### `MongoDB` configuration
Please email us if you want to setup database for this project.

## Installation
Append package directory `/path/to/Smart_Review_Summarization` into PYTHONPATH

## Run to launch `srs` web app
```
cd srs_web
sudo python srs_web.py
```
