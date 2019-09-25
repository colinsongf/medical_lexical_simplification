#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 16:13:46 2018

@author: Samuele Garda
"""

from abc import ABCMeta,abstractmethod


class AbstractComplexWordIdentifier(object,metaclass = ABCMeta):
  """
  Abstract class from which all complex word identifiers classes should inherit.
  Insure that the method for checking whether a word is complex is implemented.
  """
  
  @abstractmethod
  def is_complex():
    """
    Determine if a word is considered complex.
    
    Args:
      word (str) : word
    Return:
      res (bool) : whether the word is considered complex
    """
    pass

class DummyComplexWordIdentifier(AbstractComplexWordIdentifier):
  """
  Implements a simple complex word identifier which uses the frequency as a proxy for complexity.
  
  Frequency of word in a 'complex' and 'simple' vocabulary are combined to obtain a score.
  If that score is below a given threshold the word is considered complex.
  """

  
  def __init__(self,threshold,complex_freq,simple_freq):
    """
    Initialize DummyComplexWordIdentifier.
    
    Args:
      complex_freq (dict) : lookup complex word -> frequency
      simple_freq (dict) : lookup simple word -> frequency
      threshold (int) : threshold below which word is considered complex
    """
    
    self.complex_freq = complex_freq
    self.simple_freq = simple_freq
    self.threshold = threshold
    
  
  def is_complex(self,word):
    """
    Determine if a word is considered complex.
    
    Args:
      word (str) : word
    Return:
      res (bool) : whether the word is considered complex
    """
    
    score = self.get_complexity_score(word)
    
    res = False if score > self.threshold else True
    
    return res
  
  def get_complexity_score(self,word):
    """
    Compute complexity score. The following computes the score:
    
    .. math::
      \\frac{sf}{cf} \\times length 
      
    where `sf` is frequency in simple vocabulary, `cf` in complex and
    `length` is the number of word's charcters 
    
    Args:
      word (str) : word
    Return:
      score (int) : complexity score
    """
    
    sci_f = self.get_complex_freq(word)
    
    std_f = self.get_simple_freq(word)
    
    L = len(word)
    
    score = (sci_f / std_f ) * L

    return score
  
  def get_complex_freq(self,word):
    """
    Get word frequency in complex vocabulary
    
    Args:
      word (str) : word
    Return:
      freq (int) : word frequency
    """
    
    freq = self.complex_freq.get(word,1e-10)
    return freq
  
  def get_simple_freq(self,word):
    """
    Get word frequency in simple vocabulary
    
    Args:
      word (str) : word
    Return:
      freq (int) :  word frequency
    """
    
    freq = self.simple_freq.get(word,1e-10)
    return freq

