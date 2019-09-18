#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 11:28:27 2018

@author: Samuele Garda
"""

import argparse
import logging
import gzip
from xml.etree.cElementTree import iterparse
import smart_open
import spacy
from collections import defaultdict
from gensim.utils import to_utf8
from io_utils import IOManager as iom


logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 


def parse_args():
  
  """
  Parse command line arguments
  """
  
  parser = argparse.ArgumentParser(description='Parse Wikipedia dump')
  parser.add_argument('--input',required = True, type = str, help = "File containing wikipedia dump : XML.BZ2 format")
  parser.add_argument('--scispacy-model', required = True, type = str, help = "Path to scispacy models, e.g. `en_core_sci_md`")
  parser.add_argument('--out', required = True, type = str, help = "Output directory where store files")
  parser.add_argument('--limit',default = 1000, type = int, help = "Parse only this many examples")  
  parser.add_argument('--cores',default = 4, type = int, help = "How many cores to use")  
  
  return parser.parse_args()


def preprocess_fn(text):
  """
  Preprocess string.
  
  Args:
    text (str) : input text
  Return:
    out (list) : list of tokens 
  """
  out = [w for w in text if not (w.is_stop or w.is_space or w.is_punct)]
  return out



def abstract_extractor(files):
  """
  Generator fo pubmed abstracts extracted from .zip compressed files.
  
  Args:
    files (list) : list of .zip files containing pubmed abstracts
  
  Return:
    (generator) : generator of abstracts
    
  """
  
  for file in files:
    
    infile = gzip.GzipFile(file)
    
    elems = (elem for _, elem in iterparse(infile, events=("end",)))
    
    for elem in elems:
      
      if elem.tag == 'AbstractText':
        
        yield elem.text
      
def parse_pubmed_dump(files,nlp,min_words, process_function, processes):
  """
  Yield articles from a zip Pubmed files dump  as string.
  
  Args:
    files (list) : list of paths to zip Pubmed files
    nlp (spacy.lang) : spacy language models
    min_words (int) : skip article if it has less than this many words
    process_function (function) : preprocessing function
    processes (int) : number of cores to be used
  
  """
  
  logger.info("Start processing Pubmed articles dump")
  
  abstract_all = 0
  abstract = 0
  min_words = 50
    
  texts = abstract_extractor(files)
  
  for docno,abstract in enumerate(nlp.pipe(texts, n_threads= processes, batch_size = 10 * processes)):
    
    if abstract_all % 10000 == 0:
      logger.info("PROGRESS: at article #{} accepted {} articles".format(abstract_all, abstract))
      
    abstract_all += 1
      
    if len(abstract) < min_words:
      continue
      
    abstract += 1
        
    yield abstract
    
  logger.info("finished iterating over Pubmed corpus of {} documents with total {} articles".format(abstract, abstract_all))
  
  
if __name__ == "__main__":
  
  args = parse_args()
  
  infile = args.input
  out_dir = args.out
  limit = args.limit
  cores = args.cores
  scispacy_path = args.scispacy
  min_words = 50
  
  iom.make_dir(out_dir)
  
  out_name = iom.base_name(out_dir)
  out_path = iom.join_paths([out_dir,out_name+".txt.gz"])
  counts_path = iom.join_paths([out_dir,out_name+".freqs"])
  
  
  nlp = spacy.load(scispacy_path, disble = ["tagger","ner","parser"])
  
  pubmed_counts = defaultdict(int)
  
  
  with smart_open.open(out_path ,'wb') as fout:
    
    for docno,tokens in enumerate(parse_pubmed_dump(infile = infile,
                                                    nlp = nlp,
                                                    min_words = min_words,
                                                    process_function = preprocess_fn, 
                                                    processes = cores)):
      if limit is not None and docno > limit:
        break
      
      for tok in tokens:
        pubmed_counts[tok] += 1
      
      bytes_line = to_utf8(' '.join(tokens)) # make sure we're storing proper utf8
      fout.write(bytes_line) 
            
  logger.info("Completed processing pubmed dump")
  logger.info("Saving pubmed word frequencies at : `{}`".format(counts_path))
  iom.save_pickle(pubmed_counts,counts_path)
  
  
  
  
  
  
    