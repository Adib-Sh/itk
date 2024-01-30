"""
Input: filename = the name of a json file containing RC test IDs

Returns: unbonded_hybrids, bonded_hybrids = lists of parsed RCHybrids
from tests done in the FINISHED_HYBRID and ON_MODULE stages respectively
"""

import sys
import os
print(os.getcwd())
sys.path.append(os.sep.join(["..", ".." + os.sep]))
from parsers.RCparsers import *

import json
from os.path import exists

def getHybridsFromIDFile(filename, verbose=True, datapath=None, onlySingle=False):
        
    subtype = filename.split(os.sep)[-1][:4]
    try:
        if verbose:
            print("Loading IDs from file", filename)
        file = open(filename)
        dataJson = json.load(file)
        file.close()
    except:
        print("WARNING: File not found:", filename)
        return [], []
    
    IDDict = {}
    for serialNumber, items in dataJson.items():
        for bondState in items:
            if bondState not in IDDict.keys():
                IDDict[bondState] = []
            if onlySingle and len(items[bondState]) > 1:
                IDDict[bondState].append(items[bondState][-1])
            else:
                IDDict[bondState].extend(items[bondState])

    read_stream0 = True
    read_stream1 = True

    """
    Data parsing and filtering
    """
    if datapath is None:
        datapath = "data" + os.sep

    if verbose:
        print("Parsing unbonded hybrids")
    unbonded_hybrids = []


    #Parse test IDs as known in ITKdb
    for testid in list(set(IDDict["unbonded_itkdb_testids"])):
        filename = datapath + testid + ".json"
        if exists(filename):
            #try:
                unbonded_hybrids.append(parseRC(filename, read_stream0, read_stream1, verbose=verbose))
            #except:
                #print("Parsing failed")
        else:
            print("File not found:", filename)
            #Download from itkdb TODO
            #Then parse it
            pass

    if verbose:
        print("\nParsing bonded modules")
    bonded_hybrids = []

    for testid in list(set(IDDict["bonded_itkdb_testids"])):
        filename = datapath + testid + ".json"
        if exists(filename):
            #try:
                bonded_hybrids.append(parseRC(filename, read_stream0, read_stream1, verbose=verbose))
            #except:
                #print("Parsing failed")
        else:
            #Download from itkdb TODO
            #Then parse it
            pass
        
    return unbonded_hybrids, bonded_hybrids