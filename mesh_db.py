#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 14:47:15 2018

@author: Samuele Garda
"""

# TODO
# CREATE CLASS FOR MeSH
# FIX REPETETITIONS OF TERMS, e.g. "Postmenopausal" - "Post Menopausal"

import re
import logging
from io_utils import IOManager as iom

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 

class MeSHierarchy(object):
  """
  Class representing MeSH hierarchy. Used to query MeSH tree.
  """
  
  def __init__(self,mesh_db):
    """
    Initialize class with parsed MeSH file (lookup ID -> TERMS)
    
    Args:
      mesh_db (str) : system path to pickled parsed MeSH file
    """
    self.mesh_db = iom.load_pickle(mesh_db)
 
    
  def get_synonyms_from_ids(self,mesh_ids):
    """
    Retrieve all terms that share the same parent (synonyms = siblings)
    
    Args:
      mesh_ids (list) : list of term ids
    Return:
      synonyms (set) : all terms that have the same parent id
    """
    
    synonyms = [self.get_synonyms(mesh_id) for mesh_id in mesh_ids]
    
    synonyms = set([w for syn in synonyms for w in syn])
        
    return synonyms
    
  def get_hyperyms_from_ids(self,mesh_ids):
    """
    Retrieve all terms that are parents ID for given input IDs.
    
    Args:
      mesh_ids (list) : list of term ids
    Return:
      hypernyms (set) : all parent terms of given input IDs 
    """
    
    hypernyms = [self.get_hypernyms(mesh_id) for mesh_id in mesh_ids]
    
    hypernyms = set([w for hyp in hypernyms for w in hyp])
    
    return hypernyms
  
  def get_hyponyms_from_ids(self,mesh_ids):
    """
    Retrieve all terms that are children ID for given input IDs.
    
    Args:
      mesh_ids (list) : list of term ids
    Return:
      hyponyms (set) : all children terms of given input IDs 
    """
    
    hyponyms = [self.get_hyponyms(mesh_id) for mesh_id in mesh_ids]
    
    hyponyms = set([w for hyp in hyponyms for w in hyp])
    
    return hyponyms
  
  def get_hierarchy(self,word):
    """
    Retrive all hierarchy for a given term in MeSH, i.e. : hypernyms, synonyms and hyponyms of given term.
    
    Args:
      word (str) : MeSH term
    Return:
      hierarchy (set) : all MeSH terms found walking hierarchy tree of given word 
    """
    
    ids = self.get_ids_from_str(word)
    
    hierarchy = set.union(*[self.get_hypo_from_ids(ids),
                            self.get_hyper_from_ids(ids),
                            self.get_syn_from_ids(ids)])
    
    return hierarchy
            

  def _get_hyper_keys(self,curr_id):
    """
    Retrieve parent nodes from given MeSH id.
    
    Args:
      curr_id (str) : MeSH ID in the form C05.116.198.579
    
    Return:
      hyper_kyes (list) : list of parent nodes or marker for no parent if ID is one of the roots
    """
    
    tree = curr_id.split('.')
    
    if len(tree) == 1:
      
      hyper_keys = ['No parent']
      
    else:
    
      hyper_keys = ['.'.join(tree[0:i]) for i in range(len(tree))]
      
    return hyper_keys
  
  def get_tree_position(self,curr_id):
    """
    Retrive position in tree from ID
    
    Args:
      curr_id (str) : MeSH ID in the form C05.116.198.579
    Return:
      position (int) : depth index in the MeSH tree
    """
    
    position = len(curr_id.split('.'))
    
    return position
  

  def get_hypernyms(self,curr_id):
    """
    Retrieve parent nodes MeSH terms.
    
    Args:
      curr_id (str) : MeSH ID in the form C05.116.198.579
    Return:
      hypernyms (set) : collection of terms corresponding to parent nodes of `curr_id`
    """
    
    hyper_keys = self._get_hyper_keys(curr_id)
    
    hypernyms = set.union(*[self.mesh_db.get(parent,set()) for parent in hyper_keys])
    
    return hypernyms
  
  def get_hyponyms(self,curr_id):
    """
    Retrieve children nodes  MeSH terms.
    
    Args:
      curr_id (str) : MeSH ID in the form C05.116.198.579
    Return:
      hyponyms (set) : collection of terms corresponding to child nodes of `curr_id`
    """
    
    len_curr_id = self.get_tree_position(curr_id) 
    
    id_pattern = re.compile(curr_id)
    
    hyponyms_ids = [t if self.get_tree_position(t) > len_curr_id else 'No Child' for t in filter(id_pattern.match,self.mesh_db.keys())]
    
    hyponyms = set.union(*[self.mesh_db.get(child,set()) for child in hyponyms_ids])
    
    return hyponyms
  
  def get_synonyms(self,curr_id):
    """
    Retrieve children nodes  MeSH terms.
    
    Args:
      curr_id (str) : MeSH ID in the form C05.116.198.579
    Return:
      hyponyms (set) : collection of terms corresponding to nodes`curr_id`
    """
    
    synonyms = self.mesh_db.get(curr_id,set())
    
    return synonyms

        
  def get_ids_from_str(self,word):
    """
    Get MeSH ids corresponding to a given word. Performed via regexp search.
    
    Args:
      word (str) : query
    
    Return:
      ids (list) : list of MeSH IDs corresponding to the given word
    """
    
    r = re.compile(word)
        
    ids = [k for k,v in self.mesh_db.items() if list(filter(r.match,v))]
    
    return ids
        

if __name__ == "__main__":
  
  MeSHDB = MeSHierarchy('./data/mesh/mesh2018.pkl')
    
  mesh_ids = MeSHDB.get_ids_from_str('osteoporosis')
  
  
  out = MeSHDB.mesh_db.get(mesh_ids[0])
  
  print("Syn")
    
  synonyms = [MeSHDB.get_synonyms(mesh_id) for mesh_id in mesh_ids]
    
  print(synonyms)
    
  print("Hyper")
  hypernyms = [MeSHDB.get_hypernyms(mesh_id) for mesh_id in mesh_ids]
    
  print(hypernyms)
    
  print("Hypo")
  hyponyms = [MeSHDB.get_hyponyms(mesh_id) for mesh_id in mesh_ids]
  print(hyponyms)

  
      
