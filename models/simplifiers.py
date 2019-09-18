#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 15:17:02 2018

@author: Samuele Garda
"""

import logging
from gensim.utils import unpickle
from kenlm import Model as LanguageModel
from geniatagger import GeniaTagger 
from utils.medical.mesh import MeshDatabase
from components.complex_word_identifier import ComplexWordIdentifier
from components.generators import Word2VecGenerator,PoinGenerator
from components.selectors import SimpleScienceSelector,HierarchySelector
from components.rankers import SimpleScienceRanker,ParialBeamSearchRanker

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
    
  def getSubstitutions(self,word, context = None):
    
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
  
  
  def __init__(self,model,topn,tagger,char_ngram,mesh_db,lm):
    
    logger.info("Instatiating Word2Vec with MeSH Simplifier...")
    
    self.model = unpickle(model)
    logger.info("Loaded embeddings models from : `{}`".format(model))
    self.topn = topn
    self.tagger = GeniaTagger(tagger)
    logger.info("Loaded Genia PoS tagger from : `{}`".format(tagger))
    self.char_ngram = char_ngram
    self.mesh_db = MeshDatabase(mesh_db = mesh_db, parse = False)
    self.lm = LanguageModel(lm)
    logger.info("Loaded Language Model from `{}`".format(lm))
    self.all_words_mesh =  set([v for sublist in self.mesh_db.mesh_db.values() for v in sublist])
    
  
  def getSubstitutions(self,word,context):
    
    substitutions = Word2VecGenerator.getCandidates(model = self.model,word = word,topn = self.topn)
    
    substitutions = HierarchySelector.selectSubstitutions(word = word,
                                                          substitutions = substitutions,
                                                          char_ngram = self.char_ngram,
                                                          tagger = self.tagger,
                                                          mesh_db = self.mesh_db,
                                                          all_words_mesh = self.all_words_mesh)
    
    substitutions = ParialBeamSearchRanker.rankSubstitutions(lm = self.lm,
                                                             sentence = context,
                                                             word = word,
                                                             substitutions = substitutions)
    
    return substitutions
  
  
class PoincareSimplifier(object):
  
  
  def __init__(self,model,topn,lm):
    
    logger.info("Instatiating Word2Vec with MeSH Simplifier...")
    
    self.model = unpickle(model)
    logger.info("Loaded embeddings models from : `{}`".format(model))
    self.topn = topn
    self.lm = LanguageModel(lm)
    logger.info("Loaded Language Model from `{}`".format(lm))
    
  
  def getSubstitutions(self,word,context):
    
    substitutions = PoinGenerator.getCandidates(model = self.model,word = word,topn = self.topn)
        
    substitutions = ParialBeamSearchRanker.rankSubstitutions(lm = self.lm,
                                                             context = context,
                                                             word = word,
                                                             substitutions = substitutions)
    
    return substitutions
  
  
    
    
    
    


    
    
    
    
    
    