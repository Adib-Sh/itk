"""
Sort all the test result files in aqt/data/PRR/temp into the folder structure.
Takes submitter and institute as input.
"""
    
import glob
import json
import os
import time

from metadataHelpers import *

start = time.time()

# Gather response curve test result files
files = glob.glob("../data/PRR/temp/**/*.json", recursive=True)
RCcounter = 0
RCfiles = []
for file in files:
    if "RESPONSE" in file:
        with open(file, "r") as f:
            js = json.load(f)
        if isResponseCurve(js):
            RCcounter += 1
            RCfiles.append(file)
print(RCcounter, "new files to process.")

# Compile bulkable metadata
client = getItkdbClient()
submitter = input("Please input the name of the submitter: ")
institute = input("Please input the producing institute: ")
fileTuples = []
for file in RCfiles:
    with open(file, "r") as f:
        js = json.load(f)
    print("Processing file:", file)
    metadata = getMetadataFromJson(js, client)
    metadata["Submitter"] = submitter
    metadata["Institute"] = institute
    print(metadata)
    print()
    fileTuples.append((file, metadata))

# Build folder structure
dataPath = "../data/PRR/"
for file, metadata in fileTuples:
    path = dataPath
    if metadata["ModuleType"] in ["R3", "R4", "R5"]:
        pathKeys = ["ModuleType", "HalfModuleSN", "HybridType", "Timestamp"]    
    else:
        pathKeys = ["ModuleType", "ModuleSN", "HybridType", "Timestamp"]
    filename = file.split("/")[-1]
    for key in pathKeys:
        path += metadata[key] + "/"
        checkFolder(path)
    if os.path.exists(path + filename):
        print("Warning! Metadata not written. Skipping already existing file:\n", path+filename, "\n")
    else:
        os.rename(file, path + filename)
        with open(path + "metadata.json", "w") as f:
            json.dump(metadata, f)

print("Building module metadata...")
moduleTypes = []
moduleSNs = []
for _, metadata in fileTuples:
    moduleTypes.append(metadata["ModuleType"])
    if metadata["ModuleType"] in ["R3", "R4", "R5"]:
        moduleSNs.append(metadata["HalfModuleSN"])
    else:
        moduleSNs.append(metadata["ModuleSN"])
for moduleType, moduleSN in zip(moduleTypes, moduleSNs):
    if os.path.isdir(dataPath + moduleType):
        print("Processing", moduleType, moduleSN)
        buildModuleMetadata(moduleType, moduleSN, client)

end = time.time()
print("\nGathered number of RC files: ", len(RCfiles))
print("Elapsed time: ", end-start)
print()