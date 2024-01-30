import sys
import json

with open("noiseLimitInput.txt", "r") as f:
    lines = f.readlines()

moduleTypes = []
readingLimits = False
limits = []
for line in lines:
    line = line.strip("\n")
    if readingLimits:
        limits.append(line)
    else:
        if line == "#":
            readingLimits = True
        else:
            moduleTypes.append(line)
            
if len(moduleTypes) != len(limits):
    print("Number of module types * number of streams != number of limits! Aborting.")
    sys.exit(1)
noiseLimitDict = {}
stream = 0
for moduleType, limit in zip(moduleTypes, limits):
    if moduleType not in noiseLimitDict.keys():
        noiseLimitDict[moduleType] = {}
    noiseLimitDict[moduleType][stream] = limit
    stream = 1 - stream

print(noiseLimitDict)

with open("noiseLimits.json", "w") as f:
    json.dump(noiseLimitDict, f, indent=2)