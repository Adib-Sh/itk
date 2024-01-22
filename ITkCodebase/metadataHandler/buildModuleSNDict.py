"""
Builds a dictionary for pairing module and hybrid SNs, in the case where this is
not accessible through the DB, namely: for modules that have half modules, i.e.
R3, R4 and R5.
"""

import os
import json
    
def buildSNDict(inputFile, outputFile):

    with open(inputFile, "r") as f:
        lines = f.readlines()

    SNDict = {}
    for line in lines:
        parts = line.split("\t")
        moduleSN = parts[0]
        SNDict[moduleSN] = [parts[1], parts[2].strip("\n")]
        
    print(json.dumps(SNDict, indent=2))
    overwrite = True
    if os.path.exists(outputFile):
        overwrite = True if input("Output file already exists. Overwrite? (y/n)") == "y" else False
    if overwrite:
        print("Outputing SN dictionary:")
        print(SNDict)
        with open(outputFile, "w") as f:
            json.dump(SNDict, f, indent=2)
    else:
        print("Aborting.")
    
if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    inputFile = args[0]
    outputFile = args[1]
    buildSNDict(inputFile, outputFile)