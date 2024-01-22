import os
import glob
import json

datapath = "data/"

files = glob.glob(datapath + "*.json")

subtypeIDs = {}

couldNotAddCount = 0
numTestsDict = {}

for file in files:
    with open(file, 'r') as f:
        jsonFile = json.load(f)
        serialNumber = jsonFile['components'][0]['serialNumber']
        subtype = jsonFile['components'][0]['type']['code']
        id = jsonFile['id']
        testedAtStage = jsonFile['components'][0]['testedAtStage']['code']
    if subtype not in subtypeIDs.keys():
        subtypeIDs[subtype] = {}
        numTestsDict[subtype] = {"FINISHED_HYBRID" : 0,
                              "WIRE_BONDING" : 0,
                              "ON_MODULE" : 0}
    if serialNumber not in subtypeIDs[subtype].keys():
        subtypeIDs[subtype][serialNumber] = {"unbonded_itkdb_testids": [],
                                    "bonded_itkdb_testids" : []}
    if testedAtStage == "FINISHED_HYBRID" or testedAtStage == "WIRE_BONDING":
        subtypeIDs[subtype][serialNumber]["unbonded_itkdb_testids"].append(id)
        numTestsDict[subtype][testedAtStage] += 1
    elif testedAtStage == "ON_MODULE":
        subtypeIDs[subtype][serialNumber]["bonded_itkdb_testids"].append(id)
        numTestsDict[subtype][testedAtStage] += 1
    else:
        couldNotAddCount += 1

jsonParams = ["unbonded_itkdb_testids",
              "bonded_itkdb_testids"]
for subtype in subtypeIDs:
        outputFile = subtype + "data.json"
        if os.path.isfile("downloadScripts/jsonFiles/" + outputFile):
            print("File exists:", outputFile)
            added = 0
            with open("downloadScripts/jsonFiles/" + outputFile, 'r') as f:
                outputData = json.load(f)
            for serialNumber in subtypeIDs[subtype]:
                if serialNumber not in outputData.keys():
                    outputData[serialNumber] = subtypeIDs[subtype][serialNumber]
                else:
                    for param in jsonParams:
                        for item in subtypeIDs[subtype][serialNumber][param]:
                            if item not in outputData[serialNumber][param]:
                                outputData[serialNumber][param].append(item)
                                added += 1
            with open("downloadScripts/jsonFiles/" + outputFile, 'w') as f:
                json.dump(outputData, f)
            print("Added " + str(added) + " IDs to " + subtype + ".\n" if added > 0 else "No new files added to " + subtype + ".\n")
        else:
            print("Making file:", outputFile)
            outputData = subtypeIDs[subtype]
            with open("downloadScripts/jsonFiles/" + outputFile, 'w') as f:
                json.dump(outputData, f)

print("Found the following number of tests:")
print(json.dumps(numTestsDict, indent=2))
print(couldNotAddCount, "files could not be added due to testedAtStage not being FINISHED_HYBRID, WIRE_BONDING or ON_MODULE.")

if not os.path.exists("subtypes.txt"):
    with open("subtypes.txt", 'w') as f:
        subtypes = ""
        for subtype in subtypeIDs:
            subtypes += subtype + ","
        subtypes = subtypes[:-1]
        f.write(subtypes)