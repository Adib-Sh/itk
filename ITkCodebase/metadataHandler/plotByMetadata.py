import os
import sys
sys.path.append(os.getcwd())

from resultCollector import collectResults
from parsers.RCparsers import parseRC
from plots.ResponseCurvePlots import *

def plotByMetadata(criteria, verbose=False):

    resultFiles = collectResults(criteria)

    hybrids = []
    for file in resultFiles:
        print(file)
        hybrids.append(parseRC(file[0], verbose=verbose))

    plotRCInnseHistograms(hybrids)

if __name__ == "__main__":
    args = sys.argv[1:]
    keys = args[::2]
    values = args[1::2]
    if len(keys) != len(values):
        print("Different numbers of keys and values. Aborting.")
        sys.exit(1)
        
    criteria = {}
    verbose = False
    for pair in zip(keys, values):
        key = pair[0]
        value = pair[1]
        if key == "verbose":
            verbose = value == "True" or value == "true"
        else:
            criteria[key] = value
    
    print("Plotting test results with criteria:")
    print(criteria)
    testTuples = plotByMetadata(criteria, verbose=verbose)
    print("Found", len(testTuples), "result that match.")