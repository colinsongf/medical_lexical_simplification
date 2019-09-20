#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 15:47:18 2018

@author: Samuele Garda
"""

class Word2VecGenerator(object):
  """
  Implements substitute generator with word2vec or fasttext model.
  """
  
  def __init__(self,model,topn):
    """
    Initialize generator.
    
    Args:
      model (gensim.models.Word2Vec or gensim.models.FastText) : embeddings model
      topn (int) : number of candidates to generate
    """
    
    
    self.model = model
    self.topn = topn
  
  def get_candidates(self,word):
    """
    Retrive substitution candidates from embedding model via cosine similarity.
    
    Args:
      word (str) : complex word
    Return:
      subs (list) : substitution candidates
    """
    
    try:
      subs = [w[0].lower() for w in self.model.most_similar(word,topn = self.topn)] 
    
    except KeyError:

      subs = []
    
    return subs
  
  
class PoinGenerator(object):
  """
  Implement substitute generator with Poincare embedding model.
  """
  
  def __init__(self,model,topn):
    """
    Initialize generator.
    
    Args:
      model (gensim.models.PoincareModel) : embeddings model
      topn (int) : number of candidates to generate
    """
    self.model = model
    self.topn = topn
    
  def getCandidates(self,word):
    """
    Retrive substitution candidates from embedding model via cosine similarity.
    
    Args:
      word (str) : complex word
    Return:
      subs (list) : substitution candidates
    """
    
    try:
      
      substitutions = [w[0] for w in self.model.kv.most_similar(word,topn = self.topn)]
      
    except KeyError:
      
      substitutions = []
    
    return substitutions
  
  

