import os, sys
sys.path.append(os.getcwd())
sys.path.append("./metadataHandler/")
from parsers.RCparsers import parseRC
from plots.ResponseCurvePlots import plotRCClassified
from metadataHandler.metadataHelpers import getModuleTypes
from metadataHandler.resultCollector import collectResults
import matplotlib.pyplot as plt
import numpy as np

def main(**kwargs):

    sigmaLimit = 25

    criteria = {"HandPicked" : "Yes", "TemperatureCategory" : "Room"}
    moduleTypes = ["R3", "R4", "R5"]
    offendingModules = {}

    edgeChipsUnclassified = []
    edgeChipsClassified = []
    midChipsUnclassified = []
    midChipsClassified = []

    bins = np.linspace(0, 80, 81)
    for moduleType in moduleTypes:
        
        hybridTypeDict = getModuleTypes()
        stream = 0
        
        for hybridType in hybridTypeDict[moduleType]:
            criteria["ModuleType"] = moduleType
            criteria["HybridType"] = hybridType
            testTuples = collectResults(criteria)
            
            h = 0
            for testTuple in testTuples:
                print("Hybrid", h)
                h += 1
                hybrid = parseRC(testTuple[0])
                hybrid.serialNumber = testTuple[1]["HybridSN"]
                for c, chip in enumerate([hybrid.chips[0], hybrid.chips[-1]]):
                    sigmaInnse = chip.sigmaInnse(stream=stream, countbadchannels=False)
                    edgeChipsUnclassified.append(sigmaInnse)
                    #if sigmaInnse >= sigmaLimit:
                    #    if moduleType not in offendingModules.keys():
                    #        offendingModules[moduleType] = []
                    #    offendingModules[moduleType].append((hybrid, {0:"left ",1:"right "}[c]+"edge"+", "+str(np.round(sigmaInnse,2))))
                
                for c, chip in enumerate(hybrid.chips[1:-1]):
                    sigmaInnse = chip.sigmaInnse(stream=stream, countbadchannels=False)
                    midChipsUnclassified.append(sigmaInnse)
                    #if sigmaInnse >= sigmaLimit:
                    #    if moduleType not in offendingModules.keys():
                    #        offendingModules[moduleType] = []
                    #    offendingModules[moduleType].append((hybrid, "mid"+str(c+1)+", "+str(np.round(sigmaInnse,2))))
                
                hybrid.subtype=moduleType + hybridType
                #hybrid.classification(strategy="TypeSpecificNoSigmaReduction")
                hybrid.classification(strategy="TypeSpecific")
                for c, chip in enumerate([hybrid.chips[0], hybrid.chips[-1]]):
                    edgeChipsClassified.append(chip.sigmaInnse(stream=stream, countbadchannels=False))
                    sigmaInnse = chip.sigmaInnse(stream=stream, countbadchannels=False)
                    if sigmaInnse >= sigmaLimit:
                        if moduleType not in offendingModules.keys():
                            offendingModules[moduleType] = []
                        offendingModules[moduleType].append((hybrid, {0:"left ",1:"right "}[c]+"edge"+", "+str(np.round(sigmaInnse,2))))
                    
                for c, chip in enumerate(hybrid.chips[1:-1]):
                    midChipsClassified.append(chip.sigmaInnse(stream=stream, countbadchannels=False))
                    sigmaInnse = chip.sigmaInnse(stream=stream, countbadchannels=False)
                    if sigmaInnse >= sigmaLimit:
                        if moduleType not in offendingModules.keys():
                            offendingModules[moduleType] = []
                        offendingModules[moduleType].append((hybrid, "mid"+str(c+1)+", "+str(np.round(sigmaInnse,2))))
        
    if kwargs["mode"] == "hist":
        if True:
            fig, ax = plt.subplots()
            plt.hist(midChipsUnclassified, label={0 : "Under", 1 : "Away"}[stream]+" mid unclassified",
                    bins=bins, alpha=0.6, hatch="//////", edgecolor="darkblue", facecolor="none")
            plt.hist(edgeChipsUnclassified, label={0 : "Under", 1 : "Away"}[stream]+" edge unclassified",
                    bins=bins, color="lightblue", alpha=0.7)
            plt.title("Chip innse sigma, unclassified, stream " + {0 : "under", 1 : "away"}[stream])
            plt.legend()
            plt.axvline(x=sigmaLimit, linestyle=":", color="k", label="Barrel limit")
            plt.xlabel("Chip input noise sigma [ENC]")
            plt.ylabel("# chips")
            ax.set_facecolor("grey")
            plt.yscale("log")
            ylim = ax.get_ylim()
            ax.set_ylim(ylim[0], 100)
        
        fig, ax = plt.subplots()
        plt.title("Chip innse sigma, classified (no nSigma reduction), stream " + {0 : "under", 1 : "away"}[stream])
        plt.hist(midChipsClassified, label={0 : "Under", 1 : "Away"}[stream]+" mid classified",
                    bins=bins, alpha=0.6, hatch="//////", edgecolor="darkblue", facecolor="none")
        plt.hist(edgeChipsClassified, label={0 : "Under", 1 : "Away"}[stream]+" edge classified",
                    bins=bins, color="lightblue", alpha=0.7)
        plt.legend()
        plt.axvline(x=sigmaLimit, linestyle=":", color="k", label="Barrel limit")
        plt.xlabel("Chip input noise sigma [ENC]")
        plt.ylabel("# chips")
        ax.set_facecolor("grey")
        plt.yscale("log")
        ylim = ax.get_ylim()
        ax.set_ylim(ylim[0], 100)

    if kwargs["mode"] == "streams":
        uniqueHybrids = {}
        for moduleType in offendingModules:
                for hybrid, position in offendingModules[moduleType]:
                    if True: #hybrid.badModule:
                        if hybrid.serialNumber in uniqueHybrids.keys():
                            uniqueHybrids[hybrid.serialNumber][1] += "\n" + position
                            continue
                        else:
                            title = " ".join([moduleType, hybrid.serialNumber, "bad:", str(hybrid.badModule)])
                            title += "\n" + position
                            uniqueHybrids[hybrid.serialNumber] = [hybrid, title]
                            
        for hybridSN in uniqueHybrids:
            hybrid, title = uniqueHybrids[hybridSN]
            for comment in hybrid.fault:
                title += "\n" + comment
            if "mid" in title:
                plotRCClassified(hybrid, variable="innse", title=title,
                                showNow=False, showStats=True)

    plt.show()

if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        main(mode = args[1])
    else:
        main(mode = "hist")