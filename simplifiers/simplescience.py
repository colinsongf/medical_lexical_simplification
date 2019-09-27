#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 15:22:01 2019

@author: Samuele Garda
"""

from simplifiers.abstract_simplifier import AbstractSimplifier

class SimpleScience(AbstractSimplifier):
  """
  Lexical Simplifier with following pipeline components:
    - generator : Word2Vec or FastText embedding model
    - selector : SimpleScience selector
    - ranker : Simple Science ranker
    
  Implemented as in:
    
      Kim, Yea Seul, et al. "Simplescience: Lexical simplification of scientific terminology."
      Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing. 2016.

  """  
  
  def __init__(self,model):
    """
    Initialize SimpleScience Simplifier.
    
    Args:
      cwi (components.complex_word_identifier) : subclass of AbstractComplexWordIdentifier
      generator (components.generators) : subclass of AbstractGenerator
      selector (components.selectors.SimpleScienceSelector) : SimpleScience selector
      ranker (components.rankers.SimpleScienceRanker) : SimpleScience ranker
      model (gensim.models.*) : embedding model
      parser (spacy.lang.*) : spacy language instance
    """
    super(SimpleScience,self).__init__()
    self.model = model
    
  def simplify_word(self,word,context = None):
    
    parser = self.parser
    model = self.model
    cwi = self.cwi
    
    candidates = self.generator.get_candidates(model = model, word = word)
    
    candidates = self.selector.select_candidates(complex_word = word,
                                                 candidates = candidates,
                                                 parser = parser,
                                                 context = context,
                                                 model = model,
                                                 cwi = cwi)
    
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
        
        
    
    
    
    
    
    
    