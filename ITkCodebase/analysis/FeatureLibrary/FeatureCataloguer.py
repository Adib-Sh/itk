import sys
sys.path.append("../")
sys.path.append("../../")
from parsers.RCparsers import parseRC
from plots.ResponseCurvePlots import *
import json
import glob
import os

def addToDict(dct, key, addition):
    if addition != "":
        if not key in dct.keys():
            dct[key] = []
        additions = addition.split(" ")
        print(additions)
        dct[key].extend(additions)

subtype = "R5H1"
filename = subtype + "FeatureDict.json"

if os.path.isfile(filename):
    with open(filename, "r") as f:
        featureDict = json.load(f)
else:
    featureDict = {}

datapath = "../../data/"
jsonFiles = glob.glob(datapath + "*.json")

fig1 = None

for file in jsonFiles:
    print(file)
    hybrid = parseRC(file, verbose=False)
    if hybrid.subtype == subtype:
        hybrid.classification()
        if fig1 == None:
            (fig1, axs1) = plotRCClassified(hybrid, variable="innse")
            (fig2, axs2) = plotRCClassified(hybrid, variable="gain")
        else:
            axs1[0].clear()
            axs1[1].clear()
            axs2[0].clear()
            axs2[1].clear()
            plotRCClassified(hybrid, variable="innse", figure=(fig1, axs1))
            plotRCClassified(hybrid, variable="gain", figure=(fig2, axs2))
        fig1.show()
        fig2.show()
        features = input("Please record features (separated by whitespace) for testID " + hybrid.testID + ":\n")
        if len(hybrid.chips) == 1:
            if features == "":
                features = "CLONED"
            else:
                features = "CLONED " + features
        addToDict(featureDict, hybrid.testID, features)

with open(filename, "w") as f:
    json.dump(featureDict, f)

print(featureDict)