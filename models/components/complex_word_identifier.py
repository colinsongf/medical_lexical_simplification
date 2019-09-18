#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 16:13:46 2018

@author: Samuele Garda
"""

class ComplexWordIdentifier:
  
  @classmethod
  def getComplexityScore(cls,word,complex_freq,simple_freq):
    
    sci_f = cls.getComplexFrequency(word,complex_freq)
    
    std_f = cls.getSimpleFrequency(word,simple_freq)
    
    L = len(word)
    
    score = (sci_f / std_f ) * L
    
    return score
  
  @classmethod
  def getComplexFrequency(cls,word,complex_freq):
    
    return complex_freq.get(word,1e-8)
  
  @classmethod
  def getSimpleFrequency(cls,word,simple_freq):
    
    return simple_freq.get(word,1e-8)
 
