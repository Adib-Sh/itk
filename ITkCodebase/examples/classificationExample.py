"""
Classifies and plots the channel values of a module.

Input is a json RC test file path.
"""

import sys, os
sys.path.append(os.getcwd())
from parsers.RCparsers import parseRC
from plots.ResponseCurvePlots import *

def classificationExample(filepath):
    
    # Parse results of a test into an RCHybrid class
    hybrid = parseRC(filepath)
    
    # Run channel classification on the RCHybrid holding the test results
    hybrid.classification()
    
    # Plot spectrum of channel input noise and gain values for the hybrid in question
    plotRCClassified(hybrid, "innse", showNow=False)
    plotRCClassified(hybrid, "gain")
    
    
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        print("No input file provided - using default example.")
        filepath = os.sep.join(["data", "R0H0_18jan", "SN20USEH00000245_R0H0_20230405_560_9_RESPONSE_CURVE_PPA.json"])
    else:
        filepath = args[0]
    
    classificationExample(filepath)