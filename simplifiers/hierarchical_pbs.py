#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 15:43:06 2019

@author: Samuele Garda
"""

from simplifiers.abstract_simplifier import AbstractSimplifier

class HierarchicalPBS(AbstractSimplifier):
  """
  Lexical Simplifier with following pipeline components:
    - generator : Word2Vec or FastText embedding model
    - selector : MeSH hierarchy
    - ranker : Partial Beam Search
  """
  
  def __init__(self,model):
    """
    Initialize HierarchicalPBS Simplifier.
    
    Args:
      cwi (components.complex_word_identifier) : subclass of AbstractComplexWordIdentifier
      generator (components.generators.Word2VecGenerator) : subclass of AbstractGenerator
      selector (components.selectors.MeSHSelector) : Hierarchical selector
      ranker (components.rankers.PartialBeamSearchRanker) : Partial Beam Search ranker
      model (gensim.models.Word2Vec or gensim.models.FastText) : embedding model
      parser (spacy.lang.*) : spacy language instance
    """
    super(HierarchicalPBS,self).__init__()
    self.model = model
    
  def simplify_word(self,word,context = None,return_beams = False):
    
    parser = self.parser
    model = self.model
    
    candidates = self.generator.get_candidates(model = model, word = word)
    
    candidates = self.selector.select_candidates(complex_word = word,
                                                 candidates = candidates,
                                                 parser = parser,
                                                 context = context)
    
    candidates = self.ranker.rank_candidates(complex_word = word,
                                             candidates = candidates,
                                             context = context,
                                             return_beams = return_beams)
    
    return candidates
  
  
  def simplify_text(self,text):
    
    raise NotImplementedError("Unsupervised simplification is not implemented yet for Simplifiers with PBS ranker.")