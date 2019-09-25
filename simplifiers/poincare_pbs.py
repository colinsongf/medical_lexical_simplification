#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 15:57:34 2019

@author: Samuele Garda
"""

from simplifiers.abstract_simplifier import AbstractSimplifier

class PoincarePBS(AbstractSimplifier):
  
  def __init__(self,model):
    super(PoincarePBS,self).__init__()
    self.model = model
    
  def simplify_word(self,word,context = None,return_beams = False):
    
    model = self.model
    
    candidates = self.generator.get_candidates(model = model, word = word)
    
    candidates = self.ranker.rank_candidates(complex_word = word,
                                             candidates = candidates,
                                             context = context,
                                             return_beams = return_beams)
    
    return candidates
  
  
  def simplify_text(self,text):
    
    raise NotImplementedError("Unsupervised simplification is not implemented yet for Simplifiers with PBS ranker.")