#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 15:38:47 2019

@author: Samuele Garda
"""

from simplifiers.abstract_simplifier import AbstractSimplifier

class HierarchicalSimple(AbstractSimplifier):
  
  def __init__(self,model):
    super(HierarchicalSimple,self).__init__()
    self.model = model
    
  def simplify_word(self,word,context = None):
    
    parser = self.parser
    model = self.model
    
    candidates = self.generator.get_candidates(model = model, word = word)
    
    candidates = self.selector.select_candidates(complex_word = word,
                                                 candidates = candidates,
                                                 parser = parser,
                                                 context = context)
    
    candidates = self.ranker.rank_candidates(complex_word = word,
                                             candidates = candidates,
                                             model = model)
    
    return candidates
  
  
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