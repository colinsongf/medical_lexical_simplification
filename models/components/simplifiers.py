#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 15:17:02 2018

@author: Samuele Garda
"""

import logging
from gensim.utils import unpickle
from geniatagger import GeniaTagger 
from complex_word_identifier import ComplexWordIdentifier
from generators import Word2VecGenerator,PoinGenerator
from selectors import SimpleScienceSelector,HierarchySelector
from rankers import SimpleScienceRanker,ParialBeamSearchRanker

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 


class SimpleScienceSimplifier(object):
  
  def __init__(self,model,topn,alpha,tagger,complex_freq,simple_freq,freq_t,char_ngram):
    
    logger.info("Instatiating Simple Science Simplifier...")
    
    self.model = unpickle(model)
    logger.info("Loaded embeddings models from : `{}`".format(model))
    self.topn = topn
    self.alpha = alpha
    self.tagger = GeniaTagger(tagger)
    logger.info("Loaded Genia PoS tagger from : `{}`".format(tagger))
    self.complex_freq = unpickle(complex_freq)
    logger.info("Loaded Complex Word Frequencies from : `{}`".format(complex_freq))
    self.simple_freq = unpickle(simple_freq)
    logger.info("Loaded Simple Word Frequencies from : `{}`".format(simple_freq))
    self.freq_t = freq_t
    self.char_ngram = char_ngram
    
  def getSubstitutions(self,word):
    
    substitutions = Word2VecGenerator.getCandidates(model = self.model, word = word,topn = self.topn)
    
    substitutions = SimpleScienceSelector.selectSubstitutions(word = word,
                                                              cwi = ComplexWordIdentifier,
                                                              model = self.model,
                                                              substitutions = substitutions,
                                                              tagger = self.tagger,
                                                              alpha = self.alpha,
                                                              char_ngram = self.char_ngram,
                                                              complex_freq = self.complex_freq,
                                                              simple_freq = self.simple_freq,
                                                              freq_t = self.freq_t)
                                                              
    substitutions = SimpleScienceRanker.rankSubstitutions(word = word,
                                                          substitutions = substitutions,
                                                          model = self.model)
    
    return substitutions
  
  

class HierarchicalW2VSimplifier(object):
  
  
  def __init__(self,model):
    
    self.model = unpickle(model)
    
  
  def getSubstitutions(self,word,topn,alpha,char_ngram,tagger,mesh_db,lm,context):
    
    substitutions = Word2VecGenerator.getCandidates(self.model,word,topn)
    
    substitutions = HierarchySelector.selectSubstitutions(self.model,word,substitutions,tagger,char_ngram,mesh_db)
    
    substitutions = ParialBeamSearchRanker.rankSubstitutions(lm,context,word,substitutions)
    
    return substitutions
  
  
class HierarchicalPoinSimplifier(object):
  
  
  def __init__(self,model):
    
    self.model = unpickle(model)
    
  
  def getSubstitutions(self,word,topn,alpha,char_ngram,tagger,mesh_db,lm,context,beam_width):
    
    substitutions = PoinGenerator.getCandidates(self.model,word,topn)
        
    substitutions = ParialBeamSearchRanker.rankSubstitutions(lm,context,word,substitutions)
    
    return substitutions
  
  
    
    
    
    


    
    
    
    
    
    