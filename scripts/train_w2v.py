#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 26 11:52:48 2018

@author: Samuele Garda
"""

import os
import logging
import argparse
import itertools
from gensim.corpora import Dictionary
from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec,FastText
from evaluation import SimpleScienceEvaluation
from io_utils import IOManager as iom


logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 


def parse_arguments():
  """
  Parse command line arguments.
  """
  
  parser = argparse.ArgumentParser(description='Train Word2Vec embeddings')
  parser.add_argument('--config', required = True, type = str, help = "Path to training configuration")  
  parser.add_argument('--wiki', default = None, type = str, help = "Path to parsed wiki data")
  parser.add_argument('--pubmed', default = None, type = str, help = "Path to parsed pubmed data")
  parser.add_argument('--out', required = True, type = str, help = "Path where to store embeddings")
  parser.add_argument('--w2i', default = None, type = str, help = "Path to model")
  parser.add_argument('--eval-data', required = True, type = str, help = "Path to evaluation data")
  parser.add_argument('--cores', default = 4, type = int, help = "Number of cores to be used")
  
  return parser.parse_args()

def get_corpus(wiki_path,pubmed_path,doc_limit):
  
  data = []
  
  if wiki_path is not None:
    data.append(wiki_path)
  if pubmed_path is not None:
    data.append(pubmed_path)
  
  data = [LineSentence(c, limit = doc_limit) for c in data]
  corpus = itertools.chian.from_iterable(data)
  
  return corpus

def get_word2idx(corpus,w2i_path,keep_tokens,token_limit):
  
  if iom.check_exists(w2i_path):
    
      logger.info("Found dictionary! Loading...")
      word2id = iom.load_pickle(w2i_path)
      
  else:
      logger.info("Dictionary not found! Creating...")
      id2word = Dictionary(corpus, prune_at = 2000000)
       # filter out too freq/infreq words
      id2word.filter_extremes(keep_n=token_limit,
                              no_below = 2, 
                              keep_tokens = keep_tokens) 
      word2id = {v : k for k, v in id2word.items()} 
      iom.save_pickle(word2id,w2i_path)
  
  return word2id

def get_model(hyperparameters):
  
  if hyperparameters["model_type"] == "w2v":
    model_class = Word2Vec
  else:
    model_class = FastText
  
  model = model_class(size=hyperparameters.get("size",100),
                       min_count=0,
                       window=hyperparameters.get("window",10),
                       workers=hyperparameters.get("workers"),
                       hs=0,
                       negative=hyperparameters.get("nce",20))
  
  return model
  
  

if __name__ == "__main__":
  
  args = parse_arguments()
  
  config_path = args.config
  model_path = args.out
  wiki_path = args.wiki
  pubmed_path = args.pubmed
  w2i_path = args.w2i
  
  hp = iom.load_json(config_path)
  hp["workers"] = args.cores
  # insure that all words in found in test set are have word embedding
  hp["keep_tokens"] = SimpleScienceEvaluation(args.eval_data).get_all_words() 

  model_path = args.out
  
  full_corpus = get_corpus(wiki_path = wiki_path,
                           pubmed_path = pubmed_path,
                           doc_limit = hp.get("doc_limit", None))
  
  word2idx = get_word2idx(corpus = full_corpus,
                          w2i_path = w2i_path,
                          keep_tokens = hp.get("keep_tokens"),
                          token_limit = hp.get("token_limit", 50000)) 
  
  
  corpus = lambda: ([word for word in sentence if word in word2idx] for sentence in full_corpus)
  
  model = get_model(hyperparameters = hp)
  
  logger.info("Start training W2V model")
  
  # load model and continue training
  if iom.check_exists(model_path):
    
    logger.info("Model found! Loading...")
    
    model = iom.load_pickle(model_path)
  
  else:
    model.build_vocab(corpus())
  
  model.train(corpus(), epochs = hp.get("epochs",1), total_examples=model.corpus_count)
  
  model.word2id = {w :  v.index  for w, v in model.wv.vocab.items()}
  
  logger.info("Saving Word2Vec model at : `{}`".format(model_path))
  
  iom.save_pickle(model,model_path)
  
        

    
    
    
    
    
    