"""
For some reason, some json test result files don't have the "component" key,
which holds the hybrid serial number. Without it, the metadata scripts don't
work. This script takes a custom dictionary and just adds a "component" key
to all of the json files. It's an uggly solution.
"""

import sys
import json
import glob

def readCustomDict(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    customSNDict = {}
    for line in lines:
        parts = line.split("\t")
        code = parts[0]
        SN = parts[1].strip("\n")
        customSNDict[code] = SN
    return customSNDict

def addComponentKey(path, customDictFilename):
    customSNDict = readCustomDict(customDictFilename)
    print(customSNDict)
    jsonFiles = glob.glob(path+"/**/*RESPONSE*.json", recursive=True)
    for file in jsonFiles:
        with open(file, "r") as f:
            storedJson = json.load(f)
        if "component" in storedJson.keys():
            print("Found 'component' key in file", file)
        else:
            print("Adding 'component' key to file", file)
            for code in customSNDict:
                if code in file:
                    sn = customSNDict[code]
                    break
            print("Serial number:", sn)
            storedJson["component"] = sn
        with open(file, "w") as f:
            json.dump(storedJson, f)
    
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 2:
        print("Wrong number of input args:", args)
        sys.exit(1)
    addComponentKey(*args)