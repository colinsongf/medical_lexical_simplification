#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 15:43:06 2019

@author: Samuele Garda
"""

from simplifiers.abstract_simplifiers import AbstractSimplifier

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
    
  def simplify_word(self,word,context = None, select= True, rank = True):
    
    parser = self.parser
    model = self.model
    
    candidates = self.generator.get_candidates(model = model, word = word)
    
    if select:
      candidates = self.selector.select_candidates(complex_word = word,
                                                 candidates = candidates,
                                                 parser = parser,
                                                 context = context)
    
    if rank:
      candidates = self.ranker.rank_candidates(complex_word = word,
                                               candidates = candidates,
                                               context = context,
                                               )
    
    return candidates
  
  
  def simplify_text(self,text):
    
    hypos = ["<s> " for _ in range(self.ranker.beam_width)]
    
    for word in text:
      if self.cwi.is_complex(word):
        candidates = self.simplify_text(word, rank = False)
        hypos = [self.ranker.merge_words(h,c) for h in hypos for c in candidates] 
        hypos = self.ranker.prune_beams(hypos)
      else:
        hypos = [self.ranker.merge_words(h,word) for h in hypos]
    
    return hypos
        
    
    
  
