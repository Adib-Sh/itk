import os, sys
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+"/metadataHandler/")
from plots.ResponseCurvePlots import plotRCHistograms
from parsers.RCparsers import parseRC
from resultCollector import collectResults
from metadataHelpers import getModuleTypes
import matplotlib.pyplot as plt
import json

def pwbVersionEffect(criteria, saveFilename=None):
    testTuples = collectResults(criteria)
    if criteria["ModuleType"] == "R2":
        criteria["HybridType"] = "H0"
    hybridDict = {}
    usedSNs = []
    for testTuple in testTuples:
        metadata = testTuple[1]
        print(metadata["HybridType"])
        if metadata["HybridSN"] in usedSNs:
            print("Duplicate test found for hybrid", metadata["HybridSN"], "on module", metadata["ModuleSN"])
            continue
        
        if metadata["PWBVersion"] in ["Unknown", "N/A"]:
            print("PWBVersion", metadata["PWBVersion"], "- skipping hybrid", metadata["HybridSN"], "on module", metadata["ModuleSN"])
            continue
            
        usedSNs.append(metadata["ModuleType"]+metadata["HybridType"]+metadata["HybridSN"])
        
        hybrid = parseRC(testTuple[0])
        pwbVersion = metadata["PWBVersion"]
        if pwbVersion not in hybridDict.keys():
            hybridDict[pwbVersion] = []
        hybridDict[pwbVersion].append(hybrid)
    
    if len(hybridDict) == 0:
        
        print("No hybrids matching criteria found. Possibly the selected hybrids do not have powerboards.")
        print(criteria)
        print()
        return
    
    hybridDict = dict(sorted(hybridDict.items(), reverse=True))
    
    with open("./QCstudy/noiseLimits.json", "r") as f:
        noiseLimitDict = json.load(f)
    noiseLimit = noiseLimitDict[criteria["ModuleType"]+criteria["HybridType"]]
    
    cmap = plt.get_cmap("tab10")
    colorDict = dict(zip(["4.x", "3.1.1", "3.2", "3.2 Prime"], [cmap.colors[i] for i in range(2, 2+4)]))
    hatchDict = dict(zip(["4.x", "3.1.1", "3.2", "3.2 Prime"], [" ", "//", "////", "//////"]))
    
    for stream in [0, 1]:
        fig = None
        ax = None
        for pwbVersion in hybridDict:
            dataLabel = pwbVersion
            title = criteria["ModuleType"] + criteria["HybridType"] + " input noise, " + {0:"under", 1:"away"}[stream] + " stream\nshown per powerboard version"
            values = []
            hybrids = hybridDict[pwbVersion]
            
            fig, ax = plotRCHistograms(hybrids, variable="innse",
                                       dataLabel=dataLabel, fig=fig, ax=ax,
                                       showNow=False, streams=[stream],
                                       title=title, color=colorDict[pwbVersion],
                                       hatch=hatchDict[pwbVersion],
                                       histtype="stepfilled" if pwbVersion=="4.x" else "step")
        ylims = ax.get_ylim()
        color = "k"
        plt.axvline(x=float(noiseLimit[str(stream)]), ymin=ylims[0],
                    ymax=ylims[1],linestyle="--", color=color, label="High noise\nlimit, "+{0 : "under", 1 : "away"}[stream])
        ax.set_facecolor("lightgrey")
        plt.legend()
        plt.yscale("log")
        if saveFilename:
            fig.savefig(saveFilename+"_PWBVersion_"+criteria["ModuleType"] + criteria["HybridType"]+"_"+{0 : "under", 1 : "away"}[stream], dpi=300)
    
    print(usedSNs)
    if not saveFilename:
        plt.show()
        
def makeAllPlots(saveFilename):
    moduleTypeDict = getModuleTypes()
    criteria = {"HandPicked" : "Yes", "TemperatureCategory" : "Room"}
    for moduleType in moduleTypeDict:
        criteria["ModuleType"] = moduleType
        if moduleType == "R2":
            criteria["HybridType"] = ["H0", "H1"]
            pwbVersionEffect(criteria, saveFilename=saveFilename)
        else:
            for hybridType in moduleTypeDict[moduleType]:
                criteria["HybridType"] = hybridType
                pwbVersionEffect(criteria, saveFilename=saveFilename)

if __name__ == "__main__":
    print(sys.argv)
    if sys.argv[1] == "all":
        saveFilename = sys.argv[2] if sys.argv[2] != "-s" else sys.argv[3]
        makeAllPlots(saveFilename)
    else:
        keys = sys.argv[1::2]
        values = sys.argv[2::2]
        saveFilename = None
        if "-s" in keys:
            for k in range(len(keys)):
                if keys[k] == "-s":
                    break
            keys.pop(k)
            saveFilename = values.pop(k)
        criteria = dict(zip(keys, values))
        pwbVersionEffect(criteria, saveFilename=saveFilename)