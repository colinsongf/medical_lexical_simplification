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
  
  def __init__(self,parser,cwi,generator,selector,ranker):
    """
    Initialization signature for Simplifiers.
        
    A Simplifier class MUST have the following attributes,
    representing the four basic components of a Lexical Simplifcation pipeline:
      - cwi : identifier of complex words
      - generator : for generating  simpler words
      - selector : for selecting alternative among simpler words
      - ranker : for ranking the selected candidates
    
    It must have as well a `parser` attribute. This is a spacy language instance 
    which provides all NLP functionalities to the various pipeline components.
    
    
    The full pipeline runs in the follwing methods: `simplify_word` and `simplify_text`. 
     
    """
    self.parser = parser
    self.cwi = cwi
    self.generator = generator
    self.selector = selector
    self.ranker = ranker

  @abstractmethod
  def simplify_word():
    pass
  
  @abstractmethod
  def simplify_text(self,text):
    
    simplified_text = []
    
    for word in text:
      if self.cwi.is_complex(word):
        context = " ".join(simplified_text)
        candidates = self.simplify_word(word = word, context = context)
        top_candidate = self.get_top_candidate(candidates)
        simplified_text.append(top_candidate)
      else:
        simplified_text.append(word)
    
  