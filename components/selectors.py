#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 15:50:42 2018

@author: Samuele Garda
"""


from abc import ABCMeta,abstractmethod


class AbstractSelector(object,metaclass = ABCMeta):
  """
  Abstract class from which all complex word identifiers classes should inherit.
  Insure that the method for selecting candidates is implemented.
  """
  
  
  def __init__(self,char_ngram):
    """
    Initialize Selector.
    
    Args:
      char_ngram (int) : size of character ngrams for filtering by lemma
    """
    self.char_ngram = char_ngram
    
  def get_pos(self,word,parser,context = None):
    """
    Get Part of Speech tag of word with spacy. If context is given parse entire text.
    
    Args:
      word (str) : word
      parser (spacy.lang.*) : spacy language instance
      context (str or None) : context in which word appears
    Return:
      pos (str) : Part of Speech tag
    """
    
    if context is not None:
      pos = parser(" ".join([context,word]))[-1].pos_
    else:
      pos = parser(word)[0].pos_
      
    return pos
    
  def filter_lemma(self,complex_word,candidates):
    """
    Filter out simplification candidates that have a character ngram in common with complex word.
    
    Args:
      complex_word (str) : word
      candidates (list) : simplification candidates
    Return:
      candidates (list) : filtered simplification candidates
    """
        
    # generate list of character ngrams for a given word
    char_ngram = [complex_word[i:i+self.char_ngram] for i in range(len(complex_word)-self.char_ngram+1)]
    
    candidates = set([w for w in candidates if not any([c in w for c in char_ngram])])
        
    return candidates
  
  def filter_postag(self,complex_word,candidates,parser,context = None):
    """
    Filter out simplification candidates that do not have same PoS tag of complex word.
    
    Args:
      complex_word (str) : word
      candidates (list) : simplification candidates
      parser (spacy.lang.*) : spacy language instance
      context (str or None) : context in which word appears
    Return:
      candidates (list) : filtered simplification candidates
    """

    
    cw_pos = self.get_pos(complex_word,parser,context)
    
    candidates = set([w for w in candidates if self.get_pos(w,parser,context) == cw_pos])
    
    return candidates
  
  @abstractmethod
  def select_candidates():
    """
    Abstract method that implements selection logic
    """
    
    pass
  
class SimpleScienceSelector(AbstractSelector):
  """
  Selector as implemented in 
  
  Kim, Yea Seul, et al. "Simplescience: Lexical simplification of scientific terminology."
  Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing. 2016.
  """
  
  def __init__(self,cosine_threshold,frequency_threshold):
    """
    Initialize Selector.
    
    Args:
      cosine_threshold (int) : threshold for filtering by cosine similarity
      frequency_threshold (int) : threshold for filtering by frequency
    """
    super(SimpleScienceSelector,self).__init__()
    self.cos_thr = cosine_threshold
    self.freq_thr = frequency_threshold
  
  def filter_cos_sim(self,complex_word,model,condidates):
    """
    Filter out simplification candidates that have a cosine similarity with the
    complex word lower than a given threshold.
    
    Args:
      complex_word (str) : word
      model (gensim.models.Word2Vec) : embedding model
      candidates (list) : simplification candidates
    Return:
      candidates (list) : filtered simplification candidates
    """
    
    sub = [w for w in condidates if model.similarity(complex_word,w) > self.cos_thr]
        
    return sub
 
  def filter_complexity_score(self,complex_word,candidates,cwi):
    """
    Filter out simplification candidates that:
      - have a complexity score higher than complex word
      - have a frequency in complex vocabulary higher than a given threshold
    
    Args:
      complex_word (str) : word
      cwi (components.complex_word_identifier) : subclass of AbstractComplexWordIdentifier
      candidates (list) : simplification candidates
    Return:
      candidates (list) : filtered simplification candidates
    """
    
    cwcs = cwi.get_complexity_score(complex_word)
    
    sub = [w for w in candidates if cwi.get_complexity_score(w) < cwcs]
#    print("Complexity score threshold 1: {}".format(sub))
    
    sub = [w for w in sub if cwi.get_complex_freq(w) > self.freq_thr]
    
#    print("Complexity score threshold 2: {}".format(sub))
    
    return sub
  
  def select_candidates(self,complex_word,candidates,parser,context,model,cwi):
    """
    Implement full selection logic of SimpleScienceSelector.
    
    Args:
      complex_word (str) : word
      model (gensim.models.Word2Vec) : embedding model
      candidates (list) : simplification candidates
      parser (spacy.lang.*) : spacy language instance
      context (str or None) : context in which word appears
      cwi (components.complex_word_identifier) : subclass of AbstractComplexWordIdentifier
    Return:
      candidates (list) : filtered simplification candidates
      
    """
    
    candidates = self.filter_lemma(complex_word = complex_word,candidates = candidates)
    
    candidates = self.filter_postag(complex_word = complex_word, candidates = candidates,
                                    parser = parser, context = context)
    
    candidates = self.filter_cos_sim(complex_word = complex_word, candidates = candidates,
                                     model = model)
    
    candidates = self.filter_complexity_score(complex_word = complex_word, candidates = candidates,
                                              cwi = cwi)
    
    return candidates
  
class MeSHSelector(AbstractSelector):
  """
  Selector that exploits MeSH hierarchy, i.e. accept substitutions 
  if they are in complex word hierarchy ( hypernym, synonym or hyponym of complex word)
  """
  
  def __init__(self,mesh_db):
    """
    Initialize Selector.
    
    Args:
      mesh_db (mesh_db.MeSHierarchy) : object for querying MeSH hierarchy

    """
    super(MeSHSelector,self).__init__()
    self.mesh_db = mesh_db
    self.mesh_words = set([v for sublist in self.mesh_db.mesh_db.values() for v in sublist])
    
  def filter_mesh_hierarchy(self,complex_word,candidates):
    """
    Filter out simplification candidates that are not in MeSH hierarchy
    of complex word ( hypernym, synonym or hyponym of complex word). It is applied only if 
    complex word is a MeSH term.
    """
    
    if complex_word in self.mesh_words:
    
      hierarchy = self.mesh_db.get_hierarchy(complex_word)
      
      candidates = [s for s in candidates if s in hierarchy] if hierarchy else candidates
          
    return candidates
  
  def select_candidates(self,complex_word,candidates,parser,context):
    """
    Implement full selection logic of MeSHSelector.
    
    Args:
      complex_word (str) : word
      candidates (list) : simplification candidates
      parser (spacy.lang.*) : spacy language instance
      context (str or None) : context in which word appears
    Return:
      candidates (list) : filtered simplification candidates
      
    """
    
    candidates = self.filter_lemma(complex_word = complex_word,candidates = candidates)
    
    candidates = self.filter_postag(complex_word = complex_word, candidates = candidates,
                                    parser = parser, context = context)  
    
    candidates = self.filter_mesh_hierarchy(complex_word = complex_word, candidates = candidates)
    
    return candidates
    
    
    
    
    