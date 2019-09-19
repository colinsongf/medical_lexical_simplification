#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 12:17:09 2019

@author: Samuele Garda
"""

import argparse
import logging
import itertools
from io_utils import IOManager as iom
from mesh_db import MeSHDatabase

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO')

def parse_arguments():
  """
  Parse command line arguments.
  """
  
  parser = argparse.ArgumentParser(description='Create training data for poincare model: (term,hypernym) tuples')
  
  parser.add_argument('--mesh-dir',required = True, type = str, help = "Path to directory containing mesh files")
  parser.add_argument('--out',required = True, type = str, help = "Directory where to store output file")
  
  return parser.parse_args()

def parse_mesh_tree(path):
  """
  Parse MeSH tree file into a dictionary lookup : MeSH ID -> MeSH Unique Term
  
  Args:
    path (str) : system path to MeSH tree file
  
  Return:
    mesh_tree (dict) : MeSH ID -> MeSH Unique Term
  """
  
  mesh_tree = {}
  
  with open(path) as infile:
    for line in infile:
      term,_id = line.split(';')
      if ',' in term:
        words = term.split(',')
        term = ' '.join((words[1].strip(),words[0].strip()))
      mesh_tree[_id.strip()] = term
  
  return mesh_tree


def create_poincare_training_data(mesh_db,mesh_tree,out_path):
  """
  Generate training examples for Poincare model. Output dile contains in each line a pair (word,hypernym).
  
  Args:
    mesh_db (MeSHierarchy) : object for querying MeSH hierarchy 
    mesh_tree (dict) : lookup MeSH ID -> MeSH Unique Term
    out_path (str) : system path
  """
  
  logger.info("Storing training examples for Poincaré embeddings in `{}`".format(out_path))
  
  all_edges = set()
  
  for _id,term in mesh_tree.items():
    hyper = mesh_db.get_hypernyms(_id)
    edges = list(itertools.product([term.lower()],hyper)) 
    for edge in edges:
      all_edges.add(edge)
  
  with open(out_path, 'w+') as out_file:  
    for (i,j) in all_edges:
      out_file.write("{}\t{}\n".format(i,j))
      
      
if __name__ == "__main__":
  
  args = parse_arguments()
  
  mesh_dir = args.mesh_dir
  out_file = iom.join_paths([args.out_path,"poincare.train"])
  
  mesh_tree_path = iom.join_paths([mesh_dir,"mtrees2018.bin"])
  mesh_db_path = iom.join_paths([mesh_dir,"mesh2018.pickle"])
  
  mesh_tree = parse_mesh_tree(mesh_tree_path)
  mesh_db = MeSHDatabase(mesh_db_path)
  
  create_poincare_training_data(mesh_db = mesh_db,
                                mesh_tree = mesh_tree,
                                out_path = out_file)