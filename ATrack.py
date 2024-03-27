# Functions for analysis of the output file

import glob
import os 
import pickle

def load_MDTM_pickle(directory, prefix=None):
    """Load a droplet theory prediction pickle.
        prefix (Optional): specify a specific filename (no ext)."""
    #print("Trying with .pickle")
    if prefix==None:
        prefix1 = "MDTM_*.pickle"
    else:
        prefix1 = prefix + ".pickle"
    try:
        target = glob.glob(os.path.join(directory,prefix1))[0]
        if os.path.getsize(target)>0:
            with open(target, 'rb') as handle:
                input_dict = pickle.load(handle)
    except:
        #print("Trying .pkl")
        if prefix==None:
            prefix = "MDTM*.pkl"
        else:
            prefix = prefix[:4]+ ".pkl"
        target = glob.glob(os.path.join(directory,prefix))[0]        
        if os.path.getsize(target)>0:
            with open(target, 'rb') as handle:
                input_dict = pickle.load(handle)

    return input_dict