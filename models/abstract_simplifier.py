#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 17:33:17 2019

@author: Samuele Garda
"""

from abc import ABCMeta,abstractmethod

class AbstractSimplifier(object,metaclass = ABCMeta):
  
  def __init__(self,cwi,generator,selector,ranker):
    self.cwi = cwi
    self.generator = generator
    self.selector = selector
    self.ranker = ranker
  
  @abstractmethod
  def is_complex_word():
    pass
  
  @abstractmethod  
  def generate_substitutions():
    pass
  
  @abstractmethod
  def select_substitutions():
    pass
  
  @abstractmethod
  def rank_substitutions():
    pass
    
  