#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 17:06:57 2018

@author: Samuele Garda
"""

import pandas as pd
import logging
from collections import OrderedDict
import numpy as np
from collections import defaultdict
from nltk.tokenize import sent_tokenize
from gensim.utils import unpickle
import simplifiers
from components.complex_word_identifier import ComplexWordIdentifier


logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 

class UnsupervisedEvaluation:
  
  def __init__(self,complex_sents):
    
    self.eval_data = self.load_complex_sents(complex_sents)
  
  def load_complex_sents(self,complex_sents):
    
    sents = []
    
    with open(complex_sents) as infile:
      for line in infile:
        sents.append(line.lower().split())
    
    return sents
  
  def syllable_count(self,word):
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
    
    words = len(text)
    unique = len(set(text))
    
    o = np.log(words)
    
    ovix = o / np.log(2 - (np.log(unique) / o))
    
    return ovix
  
  def lix(self,text):
    
    words = len(text)
    sents = len(sent_tokenize(' '.join(text)))
    words_syl = sum([1 for word in text if self.syllable_count(word) > 2])
    
    lix = (words / sents) + 100 * (words_syl / words)
    
    return lix
  
  
  def flesch_kincaid_grad(self,text):
    
    num_sents = len(sent_tokenize(' '.join(text)))
    num_words = len(text)
    
    asl = num_words / num_sents
    
    syll_counts = sum([self.syllable_count(w) for w in text])
    
    aws = syll_counts / num_words
    
    fkglt = (0.39 * asl) + (11.8 * aws) - 15.59
      
    return fkglt
  
  
  def evaluate_simplifier(self,simplifier):
    
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
      
class SimpleScienceEvaluation(object):
  
  def __init__(self,eval_path,sent_path):
    
    self.eval_data = self.load_simplescience_evaluate(eval_path)
    self.sent_data = self.load_simplescience_sent_eval(sent_path)
    self.oov = ["recrudesce","suregada","keratin-8","feprazone","17-hydroxycorticosteroids"]
    
  
  def is_in_vocab(self,simplifier,word):
    
    res = False
    
    if isinstance(simplifier,simplifiers.SimpleScienceSimplifier) or isinstance(simplifier,simplifiers.HierarchicalW2VSimplifier): 
      res = word in simplifier.model
      
    elif isinstance(simplifier,simplifiers.PoincareSimplifier):
      
      res = word in simplifier.model.kv
      
    return res
        
    
  
  def load_simplescience_sent_eval(self,sent):
    
    list_dict = pd.read_csv(sent, sep = ',').to_dict('records')
    
    sent_eval = {x.get('complex_word') : x .get('context') for x in list_dict }
    
    return sent_eval
      
  def get_all_words(self):
    
    return list(self.eval_data.keys()) + list([w for sublist in self.eval_data.values() for w in sublist])
  
  def load_simplescience_evaluate(self,eval_path):
    
    
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


  def potential(self,candidates,gold):
    
    return int(any([v for v in candidates if v in gold])) 
  
  def precision(self,candidates,gold):
    
    return sum([1 for v in candidates if v in gold]) 
  
  def scores(self,candidates,gold):
    
    prec = self.precision(candidates,gold)
    pot = self.potential(candidates,gold)
    
    f1 =  2*(prec*pot)/(prec+pot + 1e-8) 
    
    return prec,pot,f1
  
  
  def evaluate_simplifier_no_context(self,simplifier):
    
    tot_prec = 0
    tot_pot = 0
    tot_f1 = 0
    tot_case = 0
    
    
    for complex_word,gold_standard in self.eval_data.items():
      
      if self.is_in_vocab(simplifier,complex_word):
    
        candidates = simplifier.getSubstitutions(complex_word,context = '')
        
        if candidates:
        
          prec,pot,f1 = self.scores(candidates,gold_standard)
          
          tot_prec += prec
          tot_pot += pot
          tot_f1 += f1
          tot_case += 1
     
    
    logger.info("Potential : {}".format(tot_pot/tot_case))
    logger.info("Prcision : {}".format(tot_prec/tot_case))
    logger.info("F1-score : {}".format(tot_f1/tot_case))
    
  def evaluate_simplifier_with_context(self,simplifier):
    
    tot_prec = 0
    tot_pot = 0
    tot_f1 = 0
    tot_case = 0
    
    
    for complex_word,context in self.sent_data.items():
      
     if self.is_in_vocab(simplifier,complex_word):
   
        if complex_word not in self.eval_data:
          continue
        
        candidates = simplifier.getSubstitutions(complex_word,context = context)
        
        if candidates:
        
          prec,pot,f1 = self.scores(candidates,self.eval_data.get(complex_word))
          
          tot_prec += prec
          tot_pot += pot
          tot_f1 += f1
          tot_case += 1
    
    logger.info("Potential : {}".format(tot_pot/tot_case))
    logger.info("Prcision : {}".format(tot_prec/tot_case))
    logger.info("F1-score : {}".format(tot_f1/tot_case))

    
  
  
    
  
    
    


      
      
      
      
      
      
      
        
      
      
    
    
  
  