#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 17:33:17 2019

@author: Samuele Garda
"""

from abc import ABCMeta,abstractmethod

class AbstractSimplifier(object,metaclass = ABCMeta):
  """
  Abstract class from which all Simplifiers should inherit.
  Define methods that a Simplifier must implement.
  """
  
  def __init__(self,cwi,generator,selector,ranker):
    """
    Initialization signature for Simplifiers.
    
    A Simplifier class must have the following attributes,
    representing the four basic components of a Lexical Simplifcation pipeline:
      - cwi : identifier of complex words
      - generator : for generating  simpler words
      - selector : for selecting alternative among simpler words
      - ranker : for ranking the selected candidates
      
    The Simplifier can then implement the logic of each component in its
    respective methods,i.e.:
      - is_complex_word
      - generate
      - select
      - rank
    
    Finally, the full pipeline runs in the follwing methods:
      
      - simplify_word : it must always have a `context` attribute, even
        if it is not used. This is done because some components may require it.
      
      - simplify_text: the simplifier must proceed in a fully
        unsupervised way, i.e. using the complex word identification component.
    """
    self.cwi = cwi
    self.generator = generator
    self.selector = selector
    self.ranker = ranker
  
  @abstractmethod
  def is_complex_word(self,word):
    """
    Determine if a word is considered complex.
    
    Args:
      word (str) : word
    Return:
      res (bool) : whether the word is considered complex
    """
    pass
  
  @abstractmethod  
  def generate(self,word, context = None):
    """
    Generate substitution candidates.
    
    Args:
      word (str) : complex word
    Return:
      candidates (list) : substitution candidates
    """
    pass
  
  @abstractmethod
  def select(self, candidates, context = None):
    """
    Remove candidates which are not suitable for simplification.
    
    Args:
      canidates (list) : substitution candidates
    Return:
      candidates (list) : pruned substitution candidates
    """
    pass
  
  @abstractmethod
  def rank(self,candidates, context = None):
    """
    Rank candidates in decreasing order of suitability for substitution.
    
    Args:
      canidates (list) : substitution candidates
    Return:
      candidates (list) : ranked substitution candidates
    """
    pass
  
  def simplify_word(self,word, context = None):
    """
    Use generator,selector and ranker 
    to return a list of substitution candidates.
    
    Args:
      word (str) : complex word
    Return:
      candidates (list) : simpler words
    """
    
    candidates = self.generate(word,context)
    candidates = self.select(candidates,context)
    candidates = self.rank(candidates,context)

    return candidates
  
  @abstractmethod
  def simplify_text():
    pass
    
  