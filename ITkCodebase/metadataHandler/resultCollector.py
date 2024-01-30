"""
Gathers sorted test result files from ../data/PRR/ based on input criteria.
Returns list of (test, metadata) tuples.
"""

import json
import glob
import sys

def matchMetadata(criteria, metadata):
    for key in criteria:
        if key not in metadata.keys():
            print("\033[93mWarning - Ignoring unknown metadata key:", key, "\033[0m")
            continue
        if isinstance(criteria[key], list):
            if metadata[key] not in criteria[key]:
                return False
        else:
            if criteria[key] != metadata[key]:
                return False
    return True

def collectResults(criteria):

    moduleType = criteria["ModuleType"]
    hybridType = criteria["HybridType"]

    dataPath = "../data/PRR/" + moduleType + "/"

    modules = glob.glob(dataPath + "*")

    metadata = {}
    testTuples = []

    for module in modules:
        with open(module + "/moduledata.json", "r") as f:
            moduleMetadata = json.load(f)
        timestamps = []
        if not isinstance(hybridType, list):
            hybridType = [hybridType]
        for ht in hybridType:
            timestamps.extend(glob.glob(module + "/" + ht + "/*"))
        for timestamp in timestamps:
            test = glob.glob(timestamp + "/*RESPONSE*.json")
            if len(test) > 1:
                print("Found more than one test file for timestamp", timestamp, "- Aborting.")
                sys.exit(1)
            with open(timestamp + "/metadata.json", "r") as f:
                testMetadata = json.load(f)
            metadata = {}
            for key in testMetadata:
                metadata[key] = testMetadata[key]
            for key in moduleMetadata:
                metadata[key] = moduleMetadata[key]
            if matchMetadata(criteria, metadata):
                testTuples.append((test[0], metadata))
    
    return testTuples

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    keys = args[::2]
    values = args[1::2]
    if len(keys) != len(values):
        print("Different numbers of keys and values. Aborting.")
        sys.exit(1)
        
    criteria = {}
    for pair in zip(keys, values):
        key = pair[0]
        value = pair[1]
        criteria[key] = value
    
    print("Finding test results with criteria:")
    print(criteria)
    testTuples = collectResults(criteria)
    print("Found", len(testTuples), "result that match.")