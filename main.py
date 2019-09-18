#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 17:57:59 2018

@author: Samuele Garda
"""

import os
import logging
import argparse
from simplifiers import SimpleScienceSimplifier,HierarchicalW2VSimplifier,PoincareSimplifier
from evaluation import UnsupervisedEvaluation,SimpleScienceEvaluation


logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 

def parse_arguments():
  
  parser = argparse.ArgumentParser(description='Run lexical simplification experiments')
  parser.add_argument('--model',required = True, type = str, help = "Directory where model is stored")
  parser.add_argument('--simplifier',required = True,choices = ('simplescience','hierw2v','poin'), type = str, help = "Path where all models are stored")
  parser.add_argument('--wiki-freq',required = True,type = str, help = "wikipedia freq folder")
  parser.add_argument('--pubmed-freq',required = True,type = str, help = "wikipedia freq folder")
  parser.add_argument('--genia',type = str, required = True, help = "Path to GeniaTagger") 
  parser.add_argument('--lm',type = str, required = True, help = "Path to language model")
  parser.add_argument('--mesh-db',type = str, required = True, help = "Path to parsed MeSH databese")
  parser.add_argument('--eval-dir',default = None,type = str, help = "Path to folder with evaluation data")

  return parser.parse_args()



if __name__ == "__main__":
    
  args = parse_arguments()
  
  MODEL = args.model
  TAGGER = args.genia
  SWF = args.wiki_freq
  CWF = args.pubmed_freq
  MESH_DB = args.mesh_db
  LM = args.lm
  EVAL_NO_CONTEXT = os.path.join(args.eval_dir,'SimpleSciGold.csv')
  EVAL_CONTEXT = os.path.join(args.eval_dir,'simple_science_sents.csv')
  EVAL_SENT = os.path.join(args.eval_dir,'complex_sents.txt')
  
  TOPN = 100
  ALPHA = 0.4
  FREQ_T = 3000
  CHAR_NGRAM = 4
  
  
  
  if args.simplifier == 'simplescience':
  
    simplifier = SimpleScienceSimplifier(model = MODEL,
                                         topn = TOPN,
                                         alpha = ALPHA,
                                         tagger = TAGGER,
                                         complex_freq = CWF,
                                         simple_freq = SWF,
                                         freq_t = FREQ_T,
                                         char_ngram = CHAR_NGRAM)
    
  elif args.simplifier == 'hierw2v':
    
    simplifier = HierarchicalW2VSimplifier(model = MODEL,
                                           topn = TOPN,
                                           tagger = TAGGER,
                                           mesh_db = MESH_DB,
                                           lm = LM,
                                           char_ngram = CHAR_NGRAM)
    
  elif args.simplifier == 'poin':
    
    simplifier = PoincareSimplifier(model = MODEL,
                                    topn = TOPN,
                                    lm = LM,
                                    char_ngram = CHAR_NGRAM)
    
  
  sse = SimpleScienceEvaluation(EVAL_NO_CONTEXT,EVAL_CONTEXT)
  us = UnsupervisedEvaluation(EVAL_SENT,CWF,SWF)
    

  logger.info("Evaluate with no context\n")
  sse.evaluate_simplifier_no_context(simplifier)
  
  logger.info("Evaluate with context\n")
  sse.evaluate_simplifier_with_context(simplifier)
  
  logger.info("Evaluate unsupervised")
  us.evaluate_simplifier(simplifier)
  
  
    
  
  
  
  
  
    
    
    
  
  
  
  