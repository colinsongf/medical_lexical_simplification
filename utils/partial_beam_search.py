#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 12:01:14 2018

@author: Samuele Garda
"""

class PartialBeamSearch(object):
  """
  Class for PartialBeamSearch.
  Implements methods :
    `search_with_lm` : peform a partial beam search
    `_prune_beams` : used for retrieving k most likely sentences under give language model
  """
  
  def __init__(self,lm_model):
    """
    Instantiate object.
  
    :params:
      lm_model (kenlm.Model) : language model loaded with kenlm library
    """
    
    self.lm = lm_model
    
  
  def merge_word(self,w1,w2):
    """
    Merge two words with final space for composing sequence
    
    :param:
      w1 (str) : word1
      w2 (str) : word2
    :return:
      Merged words
    """
    
    return w1+w2+" "

  def _prune_beams(self,hypotheses,beam_width):
    """
    From all beams (hypothesis) computes their probability under a give language model. 
    Keeps the k (`beam_width`) most likely one.
    
    :params:
      hypotheses (list) : list of strings
    :return:
      K most likely hypotheses
    """
        
    scored_hypotheses = [(hypo, self.lm.score(hypo, bos = True, eos = False)) for hypo in hypotheses]
    
#    print(sorted(scored_hypotheses , key=lambda tup: tup[1], reverse = True))
        
    beams_to_keep = sorted(scored_hypotheses , key=lambda tup: tup[1], reverse = True)[:beam_width]
            
    return [hypo[0] for hypo in beams_to_keep]

  def search_with_lm(self,sentence,simplifier,topn,beam_width):
    """
    Perform a partial beam serach for replacing complex words with simpler one. 
    The beam search is said to be partial because in the lexical simplification task not all words need to be replaced.
    The beams are expanded only for the words that should be replaced and have possible substitutions.
    
    :params:
      original (list) : tokens of original sentence
      processed (list) : PoS tagged and lemmatized original sentence 
      simplifier (utils.LexicalSimplifier) : object used to produce recommendations
      topn (int) : number of recommendation to produce for each word
    
    :return:
      best_hypothesis (str) : most likely sentence with simpler words under given language model
    
    """
    
    hypotheses = ["<s> "]
      
    for word in sentence:
        
      if not simplifier.should_simplify(word):
                    
        hypotheses = [self.merge_word(hypo,word) for hypo in hypotheses ]
                                                          
      else:
                      
        candidates = simplifier.get_candidates(word,topn = topn)
          
        hypotheses = [self.merge_word(hypo,simplifier.expand_mwe(c)) for hypo in hypotheses for c in candidates]
      
        hypotheses = self._prune_beams(hypotheses,beam_width = beam_width)
      
    print("\n\n Best Hypothesis\n\n")
    best_hypotheses = self._prune_beams(hypotheses,beam_width = 1)[0]
      
    return best_hypotheses
  
    
    
    
    
    
  
