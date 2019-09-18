#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 15:47:18 2018

@author: Samuele Garda
"""

class Word2VecGenerator(object):
  
  @staticmethod
  def getCandidates(model,word,topn):
    
    try:
      substutitions = [w[0].lower() for w in model.most_similar(word,topn = topn)] 
    
    except KeyError:

      substutitions = []
    
    return substutitions
  
  
class PoinGenerator(object):
    
  @staticmethod
  def getCandidates(model,word,topn):
    
    try:
      
      substitutions = [w[0] for w in model.kv.most_similar(word,topn = topn)]
      
    except KeyError:
      
      substitutions = []
    
    return substitutions
  
  

