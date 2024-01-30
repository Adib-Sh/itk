import sys
import os
sys.path.append(os.getcwd());
from metadataHandler.resultCollector import collectResults
from parsers.RCparsers import parseRC
import json
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

with open("../PRR/coilOrientation/coilOrientation.json", "r") as f:
    coilOrientation = json.load(f)

testTuples = []
for moduleType in ["R4", "R5"]:
    halfModuleSNs = list(coilOrientation[moduleType].keys())
    criteria = {"ModuleType" : moduleType,
                "HybridType" : "H0",
                "HalfModuleSN" : halfModuleSNs,
                "TemperatureCategory" : "Room",
                "HandPicked" : "Yes"}
    testTuples.extend(collectResults(criteria))

fig = plt.figure(figsize=(10, 8))
offsetStep = 300
offset_0 = 100
offset = offset_0
colorDict = {"edge" : "red", "mid" : "black", "unknown" : "gray"}
for testTuple in testTuples:
    hybrid = parseRC(testTuple[0])
    moduleType = testTuple[1]["ModuleType"]
    halfModuleSN = testTuple[1]["HalfModuleSN"]
    channels = hybrid.getStream(0)
    innses = np.array([channel.innse for channel in channels])
    meanInnse = np.mean(innses)
    innses -= meanInnse
    orientation = coilOrientation[moduleType][halfModuleSN]
    color = colorDict[orientation]
    plt.plot(innses + offset, '.', color=color, label=halfModuleSN + ":" + orientation)
    offset += offsetStep
    print(halfModuleSN, orientation, color)
plt.yticks([offset_0 + offsetStep * i for i in range(len(testTuples))])
ax = plt.gca()
ax.set_yticklabels([testTuple[1]["ModuleSN"] for testTuple in testTuples])
plt.subplots_adjust(left=0.2)

legendHandles = []
for orientation, color in colorDict.items():
    legendHandles.append(Line2D([0], [0], marker='o', color='w',
                         markerfacecolor=color, label=orientation))
plt.ylabel("Input noise, rescaled to arb. units")
plt.xlabel("Channel number")
plt.title("R4H0 and R5H0 input noise")
plt.legend(handles=legendHandles)
plt.ylim([0, offset+200])
plt.show()
    