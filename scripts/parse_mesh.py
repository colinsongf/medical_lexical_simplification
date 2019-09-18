#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 11:35:54 2019

@author: Samuele Garda
"""

import re
import argparse
import logging
from io_utils import IOManager as iom

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO')

def parse_arguments():
  """
  Parse command line arguments.
  """
  
  parser = argparse.ArgumentParser(description='Create lookup id -> term for MeSH')
  
  parser.add_argument('--mesh-path',required = True, type = str, help = "Path to ascii mesh file")
  
  return parser.parse_args()


ID_PATTERN = re.compile('MN = (.+)$') 
TERM_PATTERN = re.compile('MH = (.+)$')
ENTRY_PATTERN = re.compile('ENTRY = (.+)$')

def normalize_entry(entry, mode):
  """
  Preprocess node element in MeSH hierarchy file. 
  
  Args:
    entry (str) : node in MeSH hierarchy
    mode (str) : determine if node is an entry or a term 
  
  Return:
    out (str) : processed MeSH node element
  """
  
  entry = entry.replace('ENTRY = ','').strip() if mode == 'entry' else entry.replace('MH = ','').strip()
    
  if '|' in entry:
      
    entry = entry.split('|')[0]
      
  if ',' in entry:
            
    words = entry.split(',')
      
    entry = ' '.join((words[1].strip(),words[0].strip()))
  
  out = entry.lower()
  return out

def parse_terms(terms):
  """
  Preprocess all terms in MeSH node
  
  Args:
    terms (list) : list of raw MeSH terms
  
  Return:
    terms (set) : MeSH terms
    
  >>>parse_terms(['MH = Great Lakes Region'])
  >>>{'great lakes region'}
  """

  terms = set([normalize_entry(w,mode = 'term') for w in terms])
  
  return terms
  
def parse_ids(ids):
  """
  Preprocess all IDs in MeSH node
  
  Args:
    terms (list) : list of raw MeSH IDs
  
  Return:
    terms (set) : IDs
    
  >>>parse_ids(['MN = D02.033.100.291.465', 'MN = D02.092.063.291.465'])
  >>>['D02.033.100.291.465', 'D02.092.063.291.465']
  """

  ids = set([w.replace('MN = ','').strip() for w in ids])
  
  return ids

def parse_entries(entries):
  """
  Preprocess all entries in MeSH node
  
  Args:
    terms (list) : list of raw MeSH entries
  
  Return:
    terms (set) : entries
    
  >>>parse_entries(['ENTRY = Canine Teeth|T023|NON|EQV|NLM (1992)|900913|abcdef', 'ENTRY = Cuspids', 'ENTRY = Teeth, Canine'])
  >>{'canine teeth','cuspidis'}
  """

 
  entries = set([normalize_entry(w, mode = 'entry') for w in entries])
    
  return entries

def join_entries(term,entries):
  """
  Perform set union. Remove duplicates in MeSH terms and entries for single node
  
  Args:
    terms (set) : MeSH terms
    entries (set) : MeSH entries
  
  Return:
    union (set) : union of input sets
  """
  
  union = term.union(entries)
  
  return union


def parse_mesh_db(path):
  """
  Parse MeSH hierarchy into a dictoinary lookup : MeSH ID -> MeSH Terms
  
  Args:
    path (str) : system path to raw MeSH file
  
  Returns:
    mesh_db (dict) : dictionary lookup : MeSH ID -> MeSH Terms 
  """
  
  mesh_db = {}
    
  with open(path) as infile:
    
    mesh = infile.read().split('*NEWRECORD')
    
    for mesh_entry in mesh:
      lines = mesh_entry.split('\n')
      meshIds = parse_ids(filter(ID_PATTERN.match,lines))
      meshTerm = parse_terms(filter(TERM_PATTERN.match,lines))
      meshEntries = parse_entries(filter(ENTRY_PATTERN.match,lines))
      if meshIds:
        for meshId in meshIds:
          mesh_db[meshId] = join_entries(meshTerm,meshEntries)
  
  return mesh_db

if __name__ == "__main__":
  
  args = parse_arguments()
  
  mesh_path = args.mesh_path
  
  mesh_dir = iom.folder_name(mesh_path)
  mesh_db_path = iom.join_paths([mesh_dir,"mesh.pkl"])
  
  mesh_db = parse_mesh_db(mesh_path)
  
  logger.info("Saving parsed MeSH hierarchy at `{}`".format(mesh_db_path))
  iom.save_pickle(mesh_db,mesh_db_path)
  
  
  