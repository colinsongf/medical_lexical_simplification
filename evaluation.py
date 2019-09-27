#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 17:06:57 2018

@author: Samuele Garda
"""

from abc import ABCMeta,abstractmethod
import pandas as pd
import logging
from collections import OrderedDict
import numpy as np
from collections import defaultdict
from nltk.tokenize import sent_tokenize


logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 

class UnsupervisedEvaluation:
  """
  Performs unsupervised evaluation of Simplifier. 
  Given a list of tuple (complex text, text simplified) it measures the level of 
  simplification achieved on average on a sample of complex texts. 
  This is done by computing the following readability scores:
    - OVIX
    - LIX
    - Flesch–Kincaid grade level
  """
  
  
  def __init__(self,eval_path):
    """
    Initialize evaluator.
    
    Args:
      eval_path (str) : system path to evaluation data
    """
    
    self.eval_data = self.load_eval_data(eval_path)
  
  def load_eval_data(self,eval_path):
    """
    Load the evaulation data set. Each line must be a complex text/sentence.
    
    Args:
      eval_path (str) : system path to evaluation data
    
    Return:
      eval_data (list) : list of complex texts
    """
    
    eval_data = []
    
    with open(eval_data) as infile:
      for line in infile:
        eval_data.append(line.lower().split())
    
    return eval_data
  
  def syllable_count(self,word):
    """
    Count number of syllables in a word.
    
    Args:
      word (str) : word
    
    Return:
      count (int) : number of syllables
    """
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
            if word.endswith("e"):
                count -= 1
    if count == 0:
        count += 1
    return count
  
  def ovix(self,text):
    """
    Compute OVIX score of a given text.
    
    .. math::
      ovix = \\frac{log(w)}{log(2 - \\frac{log(uw)}{log(w)} ))}
      
    where `w` is the number of words and `uw` the number of unique words.
    
    Args:
      text (list) : tokenized text
    Return:
      ovix (int) : readbility score
    """
    
    words = len(text)
    unique = len(set(text))
    
    o = np.log(words)
    
    ovix = o / np.log(2 - (np.log(unique) / o))
    
    return ovix
  
  def lix(self,text):
    """
    Compute OVIX score of a given text.
    
    .. math::
      lix = \\frac{w}{s} + 100 \\times \\frac{ws}{w}
      
    where `w` is the # of words, `s` the # of sentences 
    and `ws` the # of words with more than two syllables.
    
    Args:
      text (list) : tokenized text
    Return:
      lix (int) : readbility score
    """
    
    words = len(text)
    sents = len(sent_tokenize(' '.join(text)))
    words_syl = sum([1 for word in text if self.syllable_count(word) > 2])
    
    lix = (words / sents) + 100 * (words_syl / words)
    
    return lix
  
  
  def flesch_kincaid_grad(self,text):
    """
    Compute Flesch–Kincaid grade level test.
    
    .. math::
      FKGL = (0.39 \\times \\frac{w}{s} ) + (11.8 \\times \\frac{ws}{w}) - 15.59
      
    where `w` is the # of words, `s` the # of sentences 
    and `ws` the # of syllables.
    
    Args:
      text (list) : tokenized text
    Return:
      fkglt (int) : readbility score
    """
    
    num_sents = len(sent_tokenize(' '.join(text)))
    num_words = len(text)
    
    asl = num_words / num_sents
    
    syll_counts = sum([self.syllable_count(w) for w in text])
    
    aws = syll_counts / num_words
    
    fkglt = (0.39 * asl) + (11.8 * aws) - 15.59
      
    return fkglt
  
  
  def evaluate(self,simplifier):
    """
    Compute average OVIX,LIX and Flesch–Kincaid grade level for a collection of
    complex texts and their version produced by a Simplifier.
    
    Args:
      simplifier (Simplifier) : subclass of simplifiers.abstract_simplifier.AbstractSimplifier
    """
    
    complex_scores = dict([("ovix",0),("lix",0),("fkg",0)])
    simplified_scores = dict(("ovix",0),("lix",0),("fkg",0))
  
    tot = 0
    
    for complex_txt in self.eval_data:
      
      complex_scores["ovix"] += self.ovix(complex_txt)
      complex_scores["lix"] += self.lix(complex_txt)
      complex_scores["fkg"] += self.flesch_kincaid_grad(complex_txt)
      
      simple_txt = simplifier.simplify_text(complex_txt)
          
      simplified_scores["ovix"] += self.ovix(simple_txt)
      simplified_scores["lix"] += self.lix(simple_txt)
      simplified_scores["fkg"] += self.flesch_kincaid_grad(simple_txt)
         
      tot += 1
      
    complex_scores = OrderedDict((k,complex_scores.get(k)/tot) for k in sorted(complex_scores.keys()) )
    simplified_scores = OrderedDict((k,simplified_scores.get(k)/tot) for k in sorted(simplified_scores.keys()) )
    
    logger.info("Original Average Scores : OVIX - {} , LIX - {} , FKGT - {}".format(complex_scores.get("ovix"),
                complex_scores.get("lix"),complex_scores.get("fkg")))
    
    logger.info("Simplified Average Scores : OVIX - {} , LIX - {} , FKGT - {}".format(simplified_scores.get("ovix"),
                simplified_scores.get("lix"),simplified_scores.get("fkg")))
      
    

class AbstractSupervisedEvaluation(object, metaclass = ABCMeta):
  """
  Abstract class that implements scores for supervised evaluation, i.e. when the
  correct simpler alternatives are kwnon for a given complex word.
  
  The scores for evaluation are:
    - Potential : # of instances for which at least one substitution is in gold standard
    - Precision : average # of substitutions which are in gold standard
    - F1 : harmonic mean of Potential and Precision
    
  """
  
  def __init__(self,eval_path):
    """
    Initialize Supervised evaluator with evaluation data and dictionary with scores.
    
    Args:
      eval_path (str) : system path to evaluation data
    """
    self.eval_data = self.load_eval_data(eval_path)
    
    self.scores = {"Potential" : 0.0,
                   "Precision" : 0.0,
                   "F1" : 0.0}
    
    self.tot = 0
  
  def load_simplescience_eval_data(self,eval_path):
    """
    Load SimpleScince evaluation data.
    
    Args:
      eval_path (str) : system path to evaluation data 
    """
  
    tmp = ''
    
    subs = defaultdict(list)
    
    with open(eval_path) as infile:
      for idx,line in enumerate(infile):
        
        complex_word,simple_word = line.strip().split(',')
        
        if complex_word == tmp:
          subs[complex_word].append(simple_word)
        
        else:
          tmp = complex_word
          
    return subs
  
  
  @abstractmethod
  def load_eval_data(eval_path):
    """
    Implement here the logic for loading the evaluation data.
    """
    pass
  
  @abstractmethod
  def evaluate(simplifier):
    """
    Implement here the logic for running the evaluation.
    """
    pass
  
  def potential(self,candidates,gold):
    """
    Compute Potential score, i.e.:
      # of instances for which at least one substitution is in gold standard
    
    Args:
      candidates (list) : ranked list of simplication candidates
      gold (list) : ranked list of gold simplification candidates
      
    Return:
      pot (int) : Potential score
    """
  
    
    pot =  int(any([v for v in candidates if v in gold])) 
    
    return pot
  
  def precision(self,candidates,gold):
    """
    Compute Precision score, i.e.:
      average # of substitutions which are in gold standard
    
    Args:
      candidates (list) : ranked list of simplication candidates
      gold (list) : ranked list of gold simplification candidates
      
    Return:
      prec (int) : Precision score
    """
    
    prec =  sum([1 for v in candidates if v in gold]) 
    
    return prec
  
  def f1_score(self,prec,pot):
    """
    Compute F1 score, i.e. : harmonic mean of Potential and Precision
    
    Args:
      candidates (list) : ranked list of simplication candidates
      gold (list) : ranked list of gold simplification candidates
      
    Return:
      f1 (int) : F1 score
    """
    
    f1 =  2*(prec*pot)/(prec+pot + 1e-8) 
    
    return f1
  
  def get_scores(self,candidates,gold):
    """
    Computes Potential,Precision,F1 score.
    
    Args:
      candidates (list) : ranked list of simplication candidates
      gold (list) : ranked list of gold simplification candidates
      
    Return:
      prec,pot,f1 (triple of int) : evaluation scores
    """
    
    prec = self.precision(candidates,gold)
    pot = self.potential(candidates,gold)
    f1 = self.f1_score(prec,pot)
    
    return prec,pot,f1
  
  def update_scores(self,candidates,gold):
    """
    Update internal sum of scores and increment counter of seen evaluation instances.
    
    Args:
      candidates (list) : ranked list of simplication candidates
      gold (list) : ranked list of gold simplification candidates
      
    """
    
    prec,pot,f1 = self.get_scores(candidates,gold)
    
    self.scores["Precision"] += prec
    self.scores["Potential"] += pot
    self.scores["F1"] += f1
    
    self.tot += 1
  
  def get_average_scores(self):
    """
    Return dictionary with average score once all the evaluation data set has
    been processed.
    
    """
    
    final_scores = {k : v/self.tot for k,v in self.scores}
    
    return final_scores
    
    
    
class SupervisedEvaluationNoContext(AbstractSupervisedEvaluation):
  """
  Evaluate Simplifier on a list of words using evaluation dataset as proposed by:
    
  Kim, Yea Seul, et al. "Simplescience: Lexical simplification of scientific terminology."
  Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing. 2016.
  """
  
  def load_eval_data(self,eval_path):
    eval_data = self.load_simplescience_eval_data(eval_path)
    
    return eval_data

  
  def evaluate(self,simplifier):
    """
    Evaluate Simplifier. Print out Potential, Precision, F1 score.
    
    Args:
      simplifier (Simplifier) : subclass of simplifiers.abstract_simplifier.AbstractSimplifier
      
    """
    
    for complex_word,gold_standard in self.eval_data.items():
      
      candidates = simplifier.simplify_word(complex_word)
        
      if candidates:
        self.update_scores(candidates,gold_standard)
    
    scores = self.get_average_scores()
     
    logger.info("Potential : {}".format(scores.get("Potential")))
    logger.info("Prcision : {}".format(scores.get("Precision")))
    logger.info("F1-score : {}".format(scores.get("F1")))
  


class SupervisedEvaluationWithContext(AbstractSupervisedEvaluation):
  """
  Evaluate Simplifier with context. The context in which the complex word appears
  is exploited by the Simplifier.
  """
  
  def __init__(self,simplescience_eval_path):
    super(SupervisedEvaluationWithContext,self).__init__()
    self.simplescience_eval_data = self.load_simplescience_eval_data(simplescience_eval_path)
  
  def load_eval_data(self,eval_path):
    """
    Load evaluation data.
    
    Args:
      eval_path (str) : system path to evaluation data 
    """
    
    list_dict = pd.read_csv(eval_path, sep = ',').to_dict('records')
    
    sent_eval = {x.get('complex_word') : x .get('context') for x in list_dict }
    
    return sent_eval
  
  def evaluate(self,simplifier):
    """
    Evaluate simplifier:
    
    Args:
      simplifier (Simplifier) : subclass of simplifiers.abstract_simplifier.AbstractSimplifier
    """
    
    for complex_word,context in self.sent_data.items():
      
      candidates = simplifier.simplify_word(complex_word,context = context)
      
      if candidates:
        gold_standard = self.simplescience_eval_data.get(complex_word)
        self.update_scores(candidates,gold_standard)
    
    scores = self.get_average_scores()
    
    logger.info("Potential : {}".format(scores.get("Potential")))
    logger.info("Prcision : {}".format(scores.get("Precision")))
    logger.info("F1-score : {}".format(scores.get("F1")))
