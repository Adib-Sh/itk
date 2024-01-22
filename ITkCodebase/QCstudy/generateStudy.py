import sys
import os
import json
import matplotlib.pylab as plt
sys.path.append(os.getcwd());
sys.path.append("./metadataHandler/")
from metadataHandler.metadataHelpers import getModulesForClassification, getModuleHalfModuleTypes
from plots.ResponseCurvePlots import plotClassificationStats, plotRCHistograms, plotMisclassificationRate, plotRCClassified

def generateStudy(config, saveFilename=None, plotToShow="all"):
    criteria = config["Criteria"]
    moduleType = criteria["ModuleType"]
    modules, moduleSNsUsed, hybridDict = getModulesForClassification(moduleType, criteria, returnHybrids=True)
    if config["Title"]:
        title = config["Title"]
    else:
        title = moduleType + " channel classification"
    
    if plotToShow == "all" or plotToShow == "stats":
        fig = plotClassificationStats(modules, title=title, xlabels=moduleSNsUsed, showNow=False)
        if fig and saveFilename:
                fig.savefig(saveFilename+"_"+moduleType+"_stats", dpi=300)
    
    with open("./QCstudy/noiseLimits.json", "r") as f:
        noiseLimitDict = json.load(f)
    with open("./QCstudy/unbondedCuts.json", "r") as f:
        unbondedCutsDict = json.load(f)
    
    for hybridType in hybridDict:
        if plotToShow == "all" or plotToShow == "innse":
            title = moduleType + hybridType + " input noise distributions"
            noiseLimit = noiseLimitDict[moduleType+hybridType]
            fig, ax = plt.subplots(figsize=(6,4))
            plotRCHistograms(hybridDict[hybridType], variable="innse", title=title, showNow=False, noiseLimit=noiseLimit, fig=fig, ax=ax)
            if "yScale" in config.keys():
                plt.yscale(config["yScale"])
            if fig and saveFilename:
                fig.savefig(saveFilename+"_"+moduleType+hybridType+"_innse", dpi=300)
        
        if plotToShow == "all" or plotToShow == "outnse":
            title = moduleType + hybridType + " output noise distributions"
            unbondedCuts = unbondedCutsDict[moduleType+hybridType]
            fig = plotRCHistograms(hybridDict[hybridType], variable="outnse", title=title, showNow=False, unbondedCuts=unbondedCuts)
            if "yScale" in config.keys():
                plt.yscale(config["yScale"])
            if fig and saveFilename:
                fig.savefig(saveFilename+"_"+moduleType+hybridType+"_outnse", dpi=300)
        
        if plotToShow == "all" or plotToShow == "gain":
            title = moduleType + hybridType + " gain distributions"
            gainLimits = [55, 100]
            fig = plotRCHistograms(hybridDict[hybridType], variable="gain", title=title, showNow=False, gainLimits=gainLimits)
            if "yScale" in config.keys():
                plt.yscale(config["yScale"])
            if fig and saveFilename:
                fig.savefig(saveFilename+"_"+moduleType+hybridType+"_gain", dpi=300)
        
        if plotToShow == "all" or plotToShow == "unbonded":
            subtype = moduleType + hybridType
            for stream in [0, 1]:
                fig = plotMisclassificationRate(subtype, bondedHybrids=hybridDict[hybridType], datapath="./data/", stream=stream)
                if fig and saveFilename:
                    fig.savefig(saveFilename+"_"+moduleType+hybridType+"_unbonded_"+{0:"under", 1:"away"}[stream], dpi=300)
    if not saveFilename:
        plt.show()

def generateFullGainPlot(config, saveFilename=None):
    moduleTypeConfigFiles = config["ModuleTypeConfigFiles"]
    if config["Title"]:
        title = config["Title"]
    else:
        title = "Gain distributions - all module types"
    
    fullHybridDict = {}
    for configFile in moduleTypeConfigFiles:
        moduleTypeConfig = readConfig(configFile)
        criteria = moduleTypeConfig["Criteria"]
        moduleType = criteria["ModuleType"]
        _, _, hybridDict = getModulesForClassification(moduleType, criteria, returnHybrids=True)
        fullHybridDict[moduleType] = hybridDict
    hybrids = []
    for moduleType in fullHybridDict:
        for hybridType in fullHybridDict[moduleType]:
            hybrids.extend(fullHybridDict[moduleType][hybridType])
            print("#", moduleType+ hybridType, "hybrids:", len(fullHybridDict[moduleType][hybridType]))
    gainLimits = [55, 100]
    fig, ax = plt.subplots(figsize=(10, 4))
    plotRCHistograms(hybrids, variable="gain", title=title, showNow=False, gainLimits=gainLimits, fig=fig, ax=ax)
    if "yScale" in config.keys():
        plt.yscale(config["yScale"])
    if fig and saveFilename:
        fig.savefig(saveFilename+"_fullGain", dpi=300)
    if not saveFilename:
        plt.show()

def generateFullStatistics(config, saveFilename=None):
    moduleTypeConfigFiles = config["ModuleTypeConfigFiles"]
    allModules = []
    failureDict = {}
    for configFile in moduleTypeConfigFiles:
        moduleTypeConfig = readConfig(configFile)
        criteria = moduleTypeConfig["Criteria"]
        moduleType = criteria["ModuleType"]
        failureDict[moduleType] = {"Total": 0, "Cause" : {}}
        print("Parsing", moduleType)
        modules, moduleSNsUsed = getModulesForClassification(moduleType, criteria, returnHybrids=False)
        for module, serialNumber in zip(modules, moduleSNsUsed):
            module.serialNumber = serialNumber
            module.subtype = moduleType
            if module.badModule:
                print(module.serialNumber, module.fault)
                failureDict[moduleType]["Total"] += 1
                for comment in module.fault:
                    if comment not in failureDict[moduleType]["Cause"].keys():
                        failureDict[moduleType]["Cause"][comment] = 0
                    failureDict[moduleType]["Cause"][comment] += 1
        allModules.extend(modules)
    
    if config["Title"]:
        title = config["Title"]
    else:
        title = "Classification statistics, all module types"
    
    xlabels = [module.serialNumber for module in allModules]
    kwargs = {}
    if "yLimits" in config.keys():
        kwargs["yLimits"] = config["yLimits"]
    fig = plotClassificationStats(allModules, title=title, xlabels=xlabels, showNow=False, showType=True, **kwargs)
    print(failureDict)
    
    if fig and saveFilename:
        fig.savefig(saveFilename+"_full-stats", dpi=300)
    if not saveFilename:
        plt.show()
        
def generateHybridStreams(config, saveFilename=None):
    moduleTypeConfigFiles = config["ModuleTypeConfigFiles"]
    variable = config["Variable"]
    baseTitle = ""
    if "Title" in config.keys():
        baseTitle = config["Title"] + " - "
    onlyBad = False
    if "OnlyBad" in config.keys():
        onlyBad = config["OnlyBad"]
    
    moduleTypeDict = getModuleHalfModuleTypes()
    for configFile in moduleTypeConfigFiles:
        moduleTypeConfig = readConfig(configFile)
        criteria = moduleTypeConfig["Criteria"]
        moduleType = criteria["ModuleType"]
        modules, moduleSNsUsed, hybridDict = getModulesForClassification(moduleType, criteria, returnHybrids=True)
        
        hybridCountDict = {"H0" : 0, "H1" : 0, "H2" : 0, "H3" : 0}
        for module, moduleSN in zip(modules, moduleSNsUsed):
            hybridTypes = moduleTypeDict[module.subtype]
            for hybridType in hybridTypes:
                suptitle = " ".join((moduleSN, moduleType+hybridType))
                title = baseTitle + suptitle
                hybrid = hybridDict[hybridType][hybridCountDict[hybridType]]
                hybridCountDict[hybridType] += 1
                
                # If onlyBad == true, only include hybrids of bad modules
                if onlyBad and not module.badModule:
                    continue
                fig, _ = plotRCClassified(hybrid, variable=variable, showNow=False, title=title)
                if saveFilename:
                    fig.savefig(saveFilename+"_"+suptitle.replace(" ", "-")+"-"+variable)
    if not saveFilename:
        plt.show()

def readConfig(filename):
    with open(filename, "r") as f:
        config = json.load(f)
    return config

if __name__ == "__main__":
    
    print("Endcap strip module electrical test QC study generator.")
    print("Flags:\n-c CONFIGFILE.json")
    print("-m MODE ['default', 'fullGainPlot', 'fullStatistics']")
    print("-s PLOTSAVENAME (optional)")
    print("-p PLOTTYPE (show only one type of plot from 'innse', 'outnse', 'gain', 'unbonded', 'stats')")
    
    args = sys.argv[1:]
    
    inFlag = False
    flag = ""
    inputArgs = {}
    mode = "default"
    for arg in args:
        if inFlag:
            if flag == "c":
                config = readConfig(arg)
                inputArgs["config"] = config
                inFlag = False
            elif flag == "s":
                saveFilename = arg
                inputArgs["saveFilename"] = saveFilename
                inFlag = False
            elif flag == "m":
                mode = arg
                inFlag = False
            elif flag == "p":
                plotToShow = arg
                inputArgs["plotToShow"] = plotToShow
                inFlag = False
            else:
                print("Aborting; unknown flag:", flag)
                sys.exit(1)
        elif arg[0] == "-":
            inFlag = True
            flag = arg[1]
    
    print(inputArgs)
    print(mode)
    if mode == "default":
        generateStudy(**inputArgs)
    elif mode == "fullGainPlot" or mode == "gain":
        generateFullGainPlot(**inputArgs)
    elif mode == "fullStatistics" or mode == "stats":
        generateFullStatistics(**inputArgs)
    elif mode == "hybridStreams" or mode == "streams":
        generateHybridStreams(**inputArgs)