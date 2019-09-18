#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 16:23:14 2018

@author: Samuele Garda
"""


class SimpleScienceRanker:
  
  
  @staticmethod
  def rankSubstitutions(word,substitutions,model):
    
    subs = [(sub,model.similarity(sub,word)) for sub in substitutions]
    
    subs = sorted(subs , key=lambda tup: tup[1], reverse = True)
  
    subs = [sub[0] for sub in subs]
    
#    print("Ranked : {}".format(subs))
    
    return subs
  
  

class ParialBeamSearchRanker:
  
  @classmethod  
  def merge_words(cls,w1,w2):
    
    return w1+w2+" "
  
  @classmethod
  def prune_beams(cls,lm,hypotheses,beam_width):
        
    scored_hypotheses = [(hypo, lm.score(hypo, bos = True, eos = False)) for hypo in hypotheses]
            
    beams_to_keep = sorted(scored_hypotheses , key=lambda tup: tup[1], reverse = True)[:beam_width]
                
    return [hypo[0] for hypo in beams_to_keep]
  
  @classmethod
  def rankSubstitutions(cls,lm,sentence,word,substitutions):
    
    start_hypo = sentence + " "
    
    subs = [cls.merge_words(start_hypo,sub) for sub in substitutions]
    
    subs = cls.prune_beams(lm,subs,beam_width = len(subs)) 
    
    subs = [sub.split()[-1] for sub in subs] 
        
    return subs
    
    
    
    
    
    