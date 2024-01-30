"""
Classifies and plots the mean channel values of a series of tests.

Input is a list of json RC test file paths.
"""

import glob
import json
import sys, os
sys.path.append(os.getcwd())
from parsers.RCparsers import parseRC
from plots.ResponseCurvePlots import *

def classificationExample():
    # Get a list of .json files with test results
    filepaths = glob.glob(os.sep.join(["data", "R0H0_18jan", "*.json"]))
    
    # Variable setup
    hybrids = []
    testTimes = []
    
    # Loop over .json files
    for filepath in filepaths:
        
        # Parse results of a test into an RCHybrid class
        hybrid = parseRC(filepath)
        
        # Some management to get the test time as x label
        with open(filepath, "r") as f:
            testJson = json.load(f)
        testTime = testJson["date"]
        testTime = testTime[:testTime.find(".")]
        
        testTimes.append(testTime)
        hybrids.append(hybrid)
        
    # Plot mean values of all channels in under and away streams for a series of tests
    # Possible variables: input noise = "innse", output noise = "outnse", gain = "gain"
    title = "Trend over several response curve tests"
    plotRCCycleMeans(hybrids, variable = "innse", xlabels=testTimes, title=title)
        
        
if __name__ == "__main__":

    classificationExample()