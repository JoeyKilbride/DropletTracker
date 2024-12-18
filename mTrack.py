import importlib
import os
import sys
import numpy as np
from scipy.spatial import distance

def closest_node(node, nodes):
    dist = distance.cdist([node], nodes)
    closest_index = dist.argmin()
    return closest_index

def read_config(config_dir, file):
    sys.path.insert(0, config_dir)
    #import MDL_config as config
    config=importlib.import_module(file, package=None) 
    return config

# def readBreath(d,f):
#     data = np.genfromtxt(os.path.join(d,f+".txt"), dtype =(float, float, float, float,int), skip_header=0, names=True, usecols = (0,1,2,3,5))
#     return data

def readBreath(directory, filename):
    """Reads ImageJ (FIJI) .txt data."""
    target = os.path.join(directory,filename+".txt")
    # print("reading target file: ", target)
    with open(target) as f:
        line = f.readline()
    N_columns = len(line.split())
    if '\t' in line.strip(' ')[:1]:
        columns = tuple(np.indices((N_columns+1,))[0][1:])
    else:
        columns = tuple(np.indices((N_columns,))[0])
    types = tuple([float]*N_columns)
    data = np.genfromtxt(target, dtype=types, skip_header=0, names=True, usecols = columns)
    return data