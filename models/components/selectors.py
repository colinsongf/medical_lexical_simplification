#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 15:50:42 2018

@author: Samuele Garda
"""


from abc import ABCMeta,abstractmethod


class AbstractSelector(metaclass = ABCMeta):
  
  def __init__(self,char_ngram):
    self.char_ngram = char_ngram
    
  def filter_lemma(self,complex_word,candidates):
        
    # generate list of character ngrams for a given word
    char_ngram = [complex_word[i:i+self.char_ngram] for i in range(len(complex_word)-self.char_ngram+1)]
    
    candidates = set([w for w in candidates if not any([c in w for c in char_ngram])])
        
    return candidates
  
  def filter_postag(complex_word,candidates):
    
    cw_pos = complex_word.pos_
    
    substitutions = set([w for w in substitutions if cls.get_pos(w,tagger) == pos_word])
    
    return substitutions
  
  @abstractmethod
  def selectSubstitutions(cls,word,substitutions):
    
    pass
  
class SimpleScienceSelector(Word2VecSelector):
  
  @classmethod 
  def cosine_sim_filter(cls,word,model,substitutions,alpha):
    
    sub = [w for w in substitutions if model.similarity(word,w) > alpha]
    
#    print("Cosine similarity threshold : {}".format(sub))
    
    return sub
 
  @classmethod
  def complexity_score_filter(cls,cwi,word,substitutions,complex_freq,simple_freq,freq_t):
    
    cwcs = cwi.getComplexityScore(word,complex_freq,simple_freq)
    
    sub = [w for w in substitutions if cwi.getComplexityScore(w,complex_freq,simple_freq) < cwcs]
    
    
#    print("Complexity score threshold 1: {}".format(sub))
    
    sub = [w for w in sub if cwi.getComplexFrequency(w,complex_freq) > freq_t]
    
#    print("Complexity score threshold 2: {}".format(sub))
    
    return sub
  
  
  @classmethod
  def selectSubstitutions(cls,model,cwi,word,substitutions,tagger,alpha,char_ngram,complex_freq,simple_freq,freq_t):
    
    sub = cls.share_lemma_filter(word = word,substitutions =  substitutions, char_ngram = char_ngram)
    
    sub = cls.same_pos_tag_filter(word = word,substitutions = sub,tagger = tagger)
    
    sub = cls.cosine_sim_filter(word = word, model = model,substitutions = sub,alpha = alpha)
    
    sub = cls.complexity_score_filter(word = word,cwi = cwi, substitutions = sub,
                                      complex_freq = complex_freq,simple_freq = simple_freq,freq_t = freq_t)
    
    return sub
  
class HierarchySelector(Word2VecSelector):
    
  @classmethod
  def mesh_hierarchy_filter(cls,word,substitutions,all_words_mesh,mesh_db):
    
    if word in all_words_mesh:
    
      hierarchy = mesh_db.get_hierarchy(word)
      
      sub = [s for s in substitutions if s in hierarchy] if hierarchy else substitutions
    
    else:
      
      sub  = substitutions
          
    return sub
  
  @classmethod
  def selectSubstitutions(cls,word,substitutions,char_ngram,tagger,all_words_mesh,mesh_db):
    
    sub = cls.share_lemma_filter(word = word,substitutions =  substitutions, char_ngram = char_ngram)
    
    sub = cls.same_pos_tag_filter(word = word,substitutions = sub,tagger = tagger)
    
    sub = cls.mesh_hierarchy_filter(word = word,substitutions = sub, all_words_mesh = all_words_mesh, mesh_db = mesh_db)
    
    return sub
    
    
    
    
    