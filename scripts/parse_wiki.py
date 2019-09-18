#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 12:29:09 2018

@author: Samuele Garda
"""

import argparse
import logging
import multiprocessing
import bz2
import functools
from collections import defaultdict
import smart_open
from gensim.corpora import wikicorpus
from gensim.utils import to_unicode,to_utf8,chunkize
from gensim.parsing import preprocessing as pp
from io_utils import IOManager as iom

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 

def parse_args():
  
  """
  Parse command line arguments
  """
  
  parser = argparse.ArgumentParser(description='Parse Wikipedia dump')
  parser.add_argument('--input',required = True, type = str, help = "File containing wikipedia dump : XML.BZ2 format")
  parser.add_argument('--out', required = True, type = str, help = "Output directory where store files")
  parser.add_argument('--limit',default = 1000, type = int, help = "Parse only this many examples")  
  parser.add_argument('--cores',default = 4, type = int, help = "How many cores to use")  
  
  return parser.parse_args()


# gensim preprocessing functions
FILTERS = [lambda x : x.lower(), pp.strip_tags, 
           pp.strip_punctuation, 
           pp.strip_multiple_whitespaces, pp.remove_stopwords]

def preprocess_fn(text):
  """
  Preprocess string.
  
  Args:
    text (str) : input text
  Return:
    out (list) : list of tokens 
  """
  out = pp.preprocess_string(text, filters = FILTERS) 
  return out

def process_wikipedia_article(wiki_page,preprocess_fn):
  """
  Parse single wikipedia article.
  
  Args:
    wiki_page (tuple) : tuple of (str or None, str, str)
    preprocess_fn (function) : preprocessing function
  
  Return:
    title,text (str) : tuple containing title and text of wiki page
  """
  
  title, text, page_id = wiki_page
  
  title = to_unicode(title.replace('\t', ' ')) 
    
  text = wikicorpus.filter_wiki(text)
  
  text = preprocess_fn(text)
    
  return title,text

def parse_wiki_dump(infile, min_words, process_function, processes=multiprocessing.cpu_count()-2):
  """
  Yield articles from a bz2 Wikipedia dump `infile` as (title, tokens) 2-tuples.

  Only articles of sufficient length are returned (short articles & redirects
  etc are ignored).

  Uses multiple processes to speed up the parsing in parallel.
  
  Args:
    infile (str) : path to bz2 Wikipedia dump
    min_words (int) : skip article if it has less than this many words
    process_function (function) : preprocessing function
    processes (int) : number of cores to be used

  """
    
  logger.info("Start processing Wikipedia dump `{}`".format(infile))
  articles, articles_all = 0, 0
  
  pool = multiprocessing.Pool(processes)
  # process the corpus in smaller chunks of docs, because multiprocessing.Pool
  # is dumb and would try to load the entire dump into RAM...
  texts = wikicorpus._extract_pages(bz2.BZ2File(infile))  # generator
  ignore_namespaces = 'Wikipedia Category File Portal Template MediaWiki User Help Book Draft'.split()
  for group in chunkize(texts, chunksize=10 * processes):
    for title,tokens in pool.imap(process_function, group):
      if articles_all % 10000 == 0:
        logger.info("PROGRESS: at article #{} accepted {} articles".format(articles_all, articles))
      articles_all += 1

      # article redirects and short stubs are pruned here
      if any(title.startswith(ignore + ':') for ignore in ignore_namespaces) or len(tokens) < min_words:
        continue
      
      # all good: use this article
      articles += 1
      yield title,tokens
  pool.terminate()

  logger.info("finished iterating over Wikipedia corpus of {} documents with total {} articles".format(articles, articles_all))
  
  
if __name__ == "__main__":
  
  args = parse_args()
  
  infile = args.input
  out_dir = args.out
  limit = args.limit
  cores = args.cores
  min_words = 50
  
  iom.make_dir(out_dir)
  
  out_name = iom.base_name(out_dir)
  out_path = iom.join_paths([out_dir,out_name+".txt.gz"])
  counts_path = iom.join_paths([out_dir,out_name+".freqs"])
  
  wiki_counts = defaultdict(int)
  
  process_article = functools.partial(process_wikipedia_article, preprocess_fn = preprocess_fn)
  
  with smart_open.open(out_path ,'wb') as fout:
    
    for docno,(title,tokens) in enumerate(parse_wiki_dump(infile = infile,
                                                          min_words = min_words,
                                                          process_function = process_article, 
                                                          processes = cores)):
      if limit is not None and docno > limit:
        break
      
      for tok in tokens:
        wiki_counts[tok] += 1
      
      bytes_line = to_utf8(' '.join(tokens)) # make sure we're storing proper utf8
      fout.write(bytes_line) 
            
      if limit and docno > limit:
        break
    
    logger.info("Completed processing wikipedia dump")
    logger.info("Saving english wiki word frequencies at : `{}`".format(counts_path))
    iom.save_pickle(wiki_counts,counts_path)

      
  
  
  
  
  
  
  
  
  
  