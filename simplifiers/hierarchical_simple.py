#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 15:38:47 2019

@author: Samuele Garda
"""

from simplifiers.abstract_simplifier import AbstractSimplifier

class HierarchicalSimple(AbstractSimplifier):
  """
  Lexical Simplifier with following pipeline components:
    - generator : Word2Vec or FastText embedding model
    - selector : MeSH hierarchy
    - ranker : Simple Science ranker
  """  
  def __init__(self,model):
    """
    Initialize HierarchicalSimple Simplifier.
    
    Args:
      cwi (components.complex_word_identifier) : subclass of AbstractComplexWordIdentifier
      generator (components.generators) : subclass of AbstractGenerator
      selector (components.selectors.MeSHSelector) : Hierarchical selector
      ranker (components.rankers.SimpleScienceRanker) : SimpleScience ranker
      model (gensim.models.*) : embedding model
      parser (spacy.lang.*) : spacy language instance
    """
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