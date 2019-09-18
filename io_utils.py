#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 16:02:43 2019

@author: Samuele Garda
"""

import glob
import pickle
import logging 
import json


logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO')



class IOManager:
  """
  Class with IO helper functions
  """
  
  @staticmethod
  def files_in_folder(path,extension):
    """
    Get all the files in a folder by extension, sorted.
    
    Args:
      path (str) : system path
      extension (str) : file extensions (e.g. '.txt')
    """
    
    return sorted(glob.iglob(glob.os.path.join(path,"*.{}".format(extension))))
    
  @staticmethod
  def remove_file(path):
    """
    Delete file
    
    Args:
      path (str) : system path
    """
    
    if glob.os.path.exists(path):
      glob.os.remove(path)
      
      
  @staticmethod
  def base_name(path):
    """
    Get base name of file (no full path)
    
    Args:
      path (str) : system path
    """
    
    return glob.os.path.basename(path)
  
  @staticmethod
  def folder_name(path):
    """
    Get folder name
    
    Args:
      path (str) : system path
    """
    
    return glob.os.path.dirname(path)
    
  @staticmethod
  def check_exists(path):
    """
    Check for file existance
    
    Args:
      path (str) : system path
    """
    
    return glob.os.path.exists(path)
  
  @staticmethod
  def make_dir(path):
    """
    Create folder (and subfolders if necessary)
    
    Args:
      path (str) : system path
    """
    
    if not glob.os.path.exists(path):
      glob.os.makedirs(path)
      
  @staticmethod
  def join_paths(paths):
    """
    Create full path from list of elements
    
    Args:
      paths (list) : system paths
    """
    return glob.os.path.join(*paths)
  
  def load_json(path):
    """
    Load JSON into dict
    
    Args:
      path (str) : system path
    
    Return:
      item (dict) : dictionary
    """
    
    return json.load(open(path))
  
  @staticmethod
  def save_pickle(item,path):
    """
    Save item in pickled format
    
    Args:
      item (whatever) : python object
      path (str) : system path
    """
    
    if not glob.os.path.exists(path):
  
      pickle.dump( item, open( str(path), 'wb'))
  
    else:
  
      raise ValueError("File {} already exists! Not overwriting".format(path))
      
  @staticmethod
  def load_pickle(path):
    """
    Load pickled object from file. 
    
    Args:
      path (str) : system path
    """
    
    if glob.os.path.exists(path):
    
      item = pickle.load(open(str(path), mode = "rb"))
  
    else:
      
      raise ValueError("File {} not found!".format(path))
      
    return item


