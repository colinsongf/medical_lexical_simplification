#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 18:35:17 2018

@author: Samuele Garda
"""

import logging
import argparse
import pandas as pd
from nltk.tokenize.mwe import MWETokenizer
from utils.medical.mesh import MeshDatabase

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 

def parse_args():

  """
  Parse command line arguments.
  """
  
  parser = argparse.ArgumentParser(description='Parse PubMed XML files and save pure text')
  parser.add_argument('--mesh',required = True, type = str, help = "MeSH vocabulary")
  parser.add_argument('--chv',required = True, type = str, help = "Consumer friendly vocabulary")
  
  parser.add_argument('--out',required = True, type = str, help = "Out file to store all MWE")
  
  
  return parser.parse_args() 


def load_CHV(infile):
  
  columns = ["CUI","CHV_term","UMLS_preferred_name","CHV_preferred_name","Explanation","","CHV_preferred","UMLS_preferred","Disparaged",
             "Frequency_score","Context_score","CUI_score","Combo_score","Combo_score_no_top_words","CHV_string_id","CHV_concept_id"]
  
  
  df = pd.read_csv(infile, sep = '\t', names = columns, low_memory = False)
  
  logger.info("Loaded CHV from `{}`".format(infile))
  
  return df

def mwe_iterator(mwe_file):
  
  logger.info("Loading MWE from `{}`".format(mwe_file))
  
  with open(mwe_file) as infile:
    for line in infile:
      mwe = tuple(line.strip().split())
      
      yield mwe
      
      
def generate_MWETokenizer(mwe_file):
  
  logger.info("Instatiating MWE Tokenizer with MWE from `{}`".format(mwe_file))
  
  tokenizer = MWETokenizer()
  
  for mwe in mwe_iterator(mwe_file):
    
    tokenizer.add_mwe(mwe)
  
  return tokenizer


if __name__ == "__main__":
  
  args = parse_args()
  
  MeshDB = MeshDatabase(mesh_db = args.mesh, parse = False)
  
  df = load_CHV(args.chv)


  to_write = set()

  for key,value in MeshDB.mesh_db.items():
    for v in value:
      if len(v.split()) > 1:
        to_write.add("{}\n".format(v))
    
  chv = iter(zip(df["CHV_term"],df["UMLS_preferred_name"],df["CHV_preferred_name"]))

  for terms in chv:
    
    for t in terms:
      
      try:
        if len(t.split()) > 1:
          
          to_write.add("{}\n".format(t))
      except AttributeError:
        pass
          
  with open(args.out,'w+') as outfile:
    
    for t in to_write:
      
      outfile.write(t)
          
          
        