#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 15:47:18 2018

@author: Samuele Garda
"""


from abc import ABCMeta,abstractmethod


class AbstractGenerator(object, metaclass = ABCMeta):
  """
  Abstract class from which all generator classes should inherit.
  Insure that the method for generating candidates is implemented
  """
  
  def __init__(self,topn):
    """
    Initialize Generator.
    
    Args:
      topn (int) : number of candidates to generate
    """
    self.topn = topn
  
  @abstractmethod
  def get_candidates(model,word):
    """
    Retrive substitution candidates from embedding model via cosine similarity.
    
    Args:
      model (gensim.models.*) : embeddings model
      word (str) : complex word
    Return:
      subs (list) : substitution candidates
    """
 
    pass

class Word2VecGenerator(AbstractGenerator):
  """
  Implements substitute generator with word2vec or fasttext model.
  """
  
  def __init__(self):
    super(Word2VecGenerator,self).__init__()
  
  def get_candidates(self,model,word):
    """
    Retrive substitution candidates from embedding model via cosine similarity.
    
    Args:
      model (gensim.models.Word2Vec or gensim.models.FastText) : embeddings model
      word (str) : complex word
    Return:
      subs (list) : substitution candidates
    """
    
    try:
      subs = [w[0].lower() for w in model.most_similar(word,topn = self.topn)] 
    
    except KeyError:

      subs = []
    
    return subs
  
  
class PoinGenerator(AbstractGenerator):
  """
  Implement substitute generator with Poincare embedding model.
  """
    
  def get_candidates(self,model,word):
    """
    Retrive substitution candidates from embedding model via cosine similarity.
    
    Args:
      model (gensim.models.PoincareModel) : embeddings model
      word (str) : complex word
    Return:
      subs (list) : substitution candidates
    """
    
    try:
      
      substitutions = [w[0] for w in model.kv.most_similar(word,topn = self.topn)]
      
    except KeyError:
      
      substitutions = []
    
    return substitutions
  
  

