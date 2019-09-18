#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 16:34:46 2018

@author: Samuele Garda
"""

import argparse
import logging
from gensim.models.poincare import PoincareModel, PoincareRelations
from io_utils import IOManager as iom


logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO') 


def parse_arguments():
  """
  Parse command line arguments.
  """
  
  parser = argparse.ArgumentParser(description='Train Poincarè embeddings')
  parser.add_argument('--config', required = True, type = str, help = "Path to training configuration")  
  parser.add_argument('--out', required = True, type = str, help = "Path where to store embeddings")
  parser.add_argument('--epochs', default = 50, type = int, help = "Epochs to train")
  parser.add_argument('--batch-size', default = 50, type = int, help = "Batch size")
    
  
  return parser.parse_args()

if __name__ == "__main__":
  
  args = parse_arguments()

  config_path = args.config
  model_path = args.out
  
  
  hp = iom.load_json(config_path)
  
  data_path = hp.get("input")
  
  hp["epochs"] = args.epochs
  hp["batch_size"] = args.batch_size
  
  relations = PoincareRelations(file_path= args.data, delimiter='\t')
  
  # load model and continue training
  if iom.check_exists(model_path):
    
    logger.info("Poincarè model found! Loading")
    
    model = iom.load_pickle(model_path)
  
  # create new model
  else:
    
    # get hyperparameters of model and model training
    size = hp.get("size",100)
    nce = hp.get("nce",20)
    burn_in = hp.get("burn_in",10)
    C = hp.get("C",10)
    burn_in_alpha = burn_in / C
    reg = hp.get("reg",1)
    
    model = PoincareModel(train_data= relations,
                          size= size,
                          burn_in=burn_in,
                          negative = nce,
                          burn_in_alpha = burn_in_alpha,
                          regularization_coeff = reg)
    
  
  logger.info("Training Poincare model")
  
  model.train(epochs= hp.get("epochs",10),
              print_every= hp.get("log_every",1000))
    
  
  logger.info("Saving model at `{}`".format(model_path))
  iom.save_pickle(model_path)