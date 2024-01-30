import json

with open("unbondedCuts.txt", "r") as f:
    lines = f.readlines()

cutsDict = {}
for line in lines:
    parts = line.split(" ")
    print(parts)
    subtype = parts[0]
    stream = int(parts[1])
    cut = float(parts[2].strip("\n"))
    if subtype not in cutsDict.keys():
        cutsDict[subtype] = {}
    cutsDict[subtype][stream] = cut

with open("unbondedCuts.json", "w") as f:
    json.dump(cutsDict, f, indent=2)