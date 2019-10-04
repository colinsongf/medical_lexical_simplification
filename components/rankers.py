#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 16:23:14 2018

@author: Samuele Garda
"""

from abc import ABCMeta,abstractmethod


class AbstractRanker(object,metaclass = ABCMeta):
  """
  Abstract class from which all ranker classes should inherit.
  Insure that the method for ranking candidates is implemented
  """
  
  @abstractmethod
  def rank_candidates():
    """
    Abstract method that implements ranking logic
    """
    pass


class SimpleScienceRanker(AbstractRanker):
  """
  Ranker as implemented in:
  
  Kim, Yea Seul, et al. "Simplescience: Lexical simplification of scientific terminology."
  Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing. 2016.
  """  
  
  def rank_candidates(complex_word,candidates,model):
    """
    Sort simplification candidates in decreasing cosine similarity with compelx word
    
    Args:
      complex_word (str) : word
      model (gensim.models.Word2Vec) : embedding model
      candidates (list) : simplification candidates
    Return:
      candidates (list) : ranked simplification candidates
    """
    
    candidates = [(sub,model.similarity(sub,complex_word)) for sub in candidates]
    
    candidates = sorted(candidates , key=lambda tup: tup[1], reverse = True)
  
    candidates = [sub[0] for sub in candidates]
    
#    print("Ranked : {}".format(subs))
    
    return candidates
  
  

class PartialBeamSearchRanker:
  """
  Ranker that uses BeamSearch on complex word to sort the simplification candidates
  """
  
  def __init__(self,lm,beam_width):
    """
    Initialize Ranker.
    
    Args:
      lm (kenlm.Model) : Language model interfaced with kenlm python library
      beam_width (int) : number of candidates to consider
    """
    super(PartialBeamSearchRanker,self).__init__()
    self.lm = lm
    self.beam_width = beam_width
  
    
  def merge_words(self,w1,w2):
    """
    Join two strings .
    
    Args:
      w1 (str) : first string
      w2 (str) : second string
    return:
      out (str) : joined strings
    """
    
    out = " ".join(w1,w2)
    return out 
  
  
  def prune_beams(self,hypotheses):
    """
    Implement beam search step. All simplification candidates are sorted by increasing 
    negative log-likelihood of language model given its context.
    
    Args:
      hypotheses (list) : simplification candidates
    
    Return:
      
      beams_to_keep (list) : ranked simplification candidates
    """
        
    scored_hypotheses = [(hypo, self.lm.score(hypo, bos = True, eos = False)) for hypo in hypotheses]
            
    beams_to_keep = sorted(scored_hypotheses , key=lambda tup: tup[1], reverse = True)[:self.beam_width]
          
    beams_to_keep = [hypo[0] for hypo in beams_to_keep]      
    
    return beams_to_keep
  
  
  def rank_candidates(self,comlex_word,candidates,context = None):
    """
    Sort simplification candidates decreasing by negative log-likelihood given by language model
    
    Args:
      complex_word (str) : word
      candidates (list) : simplification candidates
      context (str or None) : context in which word appears 
    Return:
      candidates (list) : ranked simplification candidates
      
    """
    
    
    if context is not None:
      start_hypo = context if context.startswith("<s>") else "<s> "+ context 
    else:  
      start_hypo = "<s>"
    
    candidates = self.prune_beams([self.merge_words(start_hypo,sub) for sub in candidates])
        
    candidates = [sub.split()[-1] for sub in candidates]
        
    return candidates
    
    
    
    
    
    