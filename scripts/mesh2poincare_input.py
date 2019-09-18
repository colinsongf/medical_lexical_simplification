#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 12:17:09 2019

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
  
  parser.add_argument('--mesh-dir',required = True, type = str, help = "Path to directory containing mesh files")
  
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