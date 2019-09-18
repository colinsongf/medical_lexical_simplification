#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 14:47:15 2018

@author: Samuele Garda
"""

# TODO
# CREATE CLASS FOR MeSH
# FIX REPETETITIONS OF TERMS, e.g. "Postmenopausal" - "Post Menopausal"

import logging
import re
import argparse
from gensim import utils
import itertools

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 




class MeshDatabase(object):
  
  def __init__(self,mesh_db,parse = False,mesh_tree = None):
    self.parse = parse
    self.mesh_db = mesh_db
    self.mesh_tree = mesh_tree
    self.id_pattern = re.compile('MN = (.+)$') 
    self.term_pattern = re.compile('MH = (.+)$')
    self.entry_pattern = re.compile('ENTRY = (.+)$')
    
    self._init_files()
    
  def _init_files(self):
    
    if self.parse:
      
      logger.info("Passed raw MeSH file : Parsing...")
      
      self.parse_mesh_db(self.mesh_db)
    
    else:
      
      logger.info("Passed parsed MeSH file : Loading...")
      self.mesh_db = utils.unpickle(self.mesh_db)
    
    if self.mesh_tree:
      
      logger.info("Passed MeSH Tree file : Loading...")
      
      self.parse_mesh_tree(self.mesh_tree)
      
 
  def normalize_entry(self,entry, mode):
    
    entry = entry.replace('ENTRY = ','').strip() if mode == 'entry' else entry.replace('MH = ','').strip()
    
#    if '-' in entry:
#      
#      entry = ' '.join(entry.split('-'))
      
    if '|' in entry:
        
      entry = entry.split('|')[0]
        
    if ',' in entry:
              
      words = entry.split(',')
        
      entry = ' '.join((words[1].strip(),words[0].strip()))
      
    return entry.lower()
  
  def get_syn_from_ids(self,mesh_ids):
    
    synonyms = [self.get_synonyms(mesh_id) for mesh_id in mesh_ids]
    
    synonyms = set([w for syn in synonyms for w in syn])
        
    return synonyms
    
  def get_hyper_from_ids(self,mesh_ids):
    
    hypernyms = [self.get_hypernyms(mesh_id) for mesh_id in mesh_ids]
    
    hypernyms = set([w for hyp in hypernyms for w in hyp])
    
    return hypernyms
  
  def get_hypo_from_ids(self,mesh_ids):
    
    hyponyms = [self.get_hyponyms(mesh_id) for mesh_id in mesh_ids]
    
    hyponyms = set([w for hyp in hyponyms for w in hyp])
    
    return hyponyms
  
  def get_hierarchy(self,w1):
    
    ids = self.get_from_str(w1)
    
    hierarchy = set.union(*[self.get_hypo_from_ids(ids) ,self.get_hyper_from_ids(ids), self.get_syn_from_ids(ids)])
    
    return hierarchy
            

  def _get_hyper_keys(self,curr_id):
    
    tree = curr_id.split('.')
    
    if len(tree) == 1:
      
      hyper_keys = ['No parent']
      
    else:
    
      hyper_keys = ['.'.join(tree[0:i]) for i in range(len(tree))]
      
    return hyper_keys
  

  def get_hypernyms(self,curr_id):
    
    hyper_keys = self._get_hyper_keys(curr_id)
    
    hypernyms = set.union(*[self.mesh_db.get(parent,set()) for parent in hyper_keys])
    
    return hypernyms
  
  def get_tree_position(self,curr_id):
    
    return len(curr_id.split('.'))
  
  def get_hyponyms(self,curr_id):
    
    len_curr_id = self.get_tree_position(curr_id) 
    
    id_pattern = re.compile(curr_id)
    
    hyponyms_ids = [t if self.get_tree_position(t) > len_curr_id else 'No Child' for t in filter(id_pattern.match,self.mesh_db.keys())]
    
    hyponyms = set.union(*[self.mesh_db.get(child,set()) for child in hyponyms_ids])
    
    return hyponyms
  
  def get_synonyms(self,curr_id):
    
    return self.mesh_db.get(curr_id,set())
  

  
  def prune_entries(self,entries):
    
    pruned = set()
    
    for w in entries:
      if w.endswith('s') and w.replace('s','') in entries:
#        print("Ends with `s` : `{}`! Replace with `{}`".format(w, w.replace('s','')))
        pruned.add(w.replace('s',''))
      elif w.endswith('es') and w.replace('es','is') in entries:
#        print("Ends with `es` : `{}`! Replace with `{}`".format(w, w.replace('es','is')))
        pruned.add(w.replace('es','is'))
      else:
        pruned.add(w)
        
    return pruned
    
        
        
  def get_from_str(self,word):
    
    r = re.compile(word)
    
#    r = re.compile(".*({}|{}){}.*".format(word[0].capitalize(),word[0].lower(),word[1:]))
    
    ids = [k for k,v in self.mesh_db.items() if list(filter(r.match,v))]
    
    return ids
        
      
  def poin_training(self,out_path):
    
    logger.info("Storing training examples for Poincaré embeddings in `{}`".format(out_path))
    
    all_edges = set()
    
    for _id,term in self.mesh_tree.items():
#      syns = self.mesh_db.get(_id)
      hyper = self.get_hypernyms(_id)
      edges = list(itertools.product([term.lower()],hyper)) 
      for edge in edges:
        all_edges.add(edge)
    
    with open(out_path, 'w+') as out_file:  
      for (i,j) in all_edges:
        out_file.write("{}\t{}\n".format(i,j))
      
if __name__ == "__main__":
  
  args = parse_arguments()
  
  if args.mode == 'parse':
  
    MeshDB = MeshDatabase(mesh_db = args.mesh, mesh_tree = args.mesh_tree,
                          parse = True)
    
    
    utils.pickle(MeshDB.mesh_db,args.out)

    
  elif args.mode == 'poin':
    
    if not args.mesh_tree:
      raise ValueError("You need to pass `--mesh-tree` the mesh tree file!")
    
    MeshDB = MeshDatabase(mesh_db = args.mesh, mesh_tree = args.mesh_tree,
                          parse = False)
    
#    mesh_ids = MeshDB.get_from_str('osteoporosis')
#    
#    print("Syn")
#    
#    synonyms = [MeshDB.get_synonyms(mesh_id) for mesh_id in mesh_ids]
#    
#    print(synonyms)
    
#    print("Hyper")
#    hypernyms = [MeshDB.get_hypernyms(mesh_id) for mesh_id in mesh_ids]
#    
#    print(hypernyms)
#    
#    print("Hypo")
#    hyponyms = [MeshDB.get_hyponyms(mesh_id) for mesh_id in mesh_ids]
#    print(hyponyms)
        
    MeshDB.poin_training(args.out)
    
  else:
    
    raise ValueError("`--mode` argument not recognized!")
  
 
  
  
 
