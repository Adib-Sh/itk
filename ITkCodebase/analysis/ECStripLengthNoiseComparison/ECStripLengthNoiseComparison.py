import sys
sys.path.append("../../")
sys.path.append("../")
from Helpers.getHybridsFromIDFile import *
from plots.ResponseCurvePlots import *
import matplotlib.pyplot as plt
import numpy as np
import glob
from barrelData import getBarrelHybrids

def ECStripLengthNoiseComparison(*filenames, variable="innse", verbose=True, figsize=None, showHist=True, showComp=True, streams=[0, 1]):
    
    if isinstance(filenames[0], list):
        filenames = list(*filenames)
    else:
        filenames = list(filenames)
        
    if not isinstance(streams, list):
        streams = [streams]

    unbonded_hybrids = {}
    hybrids = {}
    subtypes = []
    allBarrelSubtypes = ["SSX", "SSY", "LSX", "LSY"]
    with open("../Helpers/subtypes.txt", 'r') as f:
        allECSubtypes = f.read().split(',')
    allSubtypes = []
    allSubtypes.extend(allECSubtypes)
    allSubtypes.extend(allBarrelSubtypes)
    for f, filename in enumerate(filenames):
        if "." not in "filename":
            subtype = filename
            if subtype not in allSubtypes:
                print("\nSubtype doesn't exist:", subtype, "\n")
                continue
            filenames[f] = filename + "data.json"
            
        else:
            subtype = filename.strip('data.json')
            if subtype not in allSubtypes:
                print("\nSubtype doesn't exist:", subtype, "\n")
                continue
        
        subtypes.append(subtype)
        if subtype in allECSubtypes:
            #unbonded_hybrids[subtype], hybrids[subtype] = getHybridsFromIDFile(filenames[f], verbose=verbose)
            unbonded_hybrids[subtype], hybrids[subtype] = getHybridsFromIDFile(filenames[f], verbose=verbose)
        elif subtype in allBarrelSubtypes:
            unbonded_hybrids[subtype] = []
            hybrids[subtype] = getBarrelHybrids(subtype, verbose=verbose)
        else:
            unbonded_hybrids[subtype] = []
            hybrids[subtype] = []

    subtypes.sort()
    
    lengthDict = {}
    with open("stripLengths.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        subtype, stream, _, length = line.replace(' ', '').strip('\n').split('\t')
        lengthDict[subtype+stream] = length

    fig = None
    if showHist and np.array([len(hybrids[subtype]) for subtype in subtypes]).any():
        if figsize is None:
            fig = plt.figure()
        else:
            fig = plt.figure(figsize=figsize)
        
    valueLimits = {"innse"  : [400, 3000],
                   "outnse" : [1, 30],
                   "gain"   : [10, 500]}
    bins = np.linspace(valueLimits[variable][0], valueLimits[variable][1], 120)
    meansDict = {}
    stdsDict = {}
    for subtype in subtypes:
        meansDict[subtype] = [None, None]
        stdsDict[subtype] = [None, None]
        if len(hybrids[subtype]) == 0:
            print("\nWARNING: No hybrids for subtype", subtype)
            continue
        
        print("\nNumber of", subtype, "hybrids:", len(hybrids[subtype]))
        print("Subtype", subtype, "has strip lengths", lengthDict[subtype+'away'], lengthDict[subtype+'under'])
        values = [[], []]
        for hybrid in hybrids[subtype]:
            streamDict = {0 : hybrid.stream0, 1 : hybrid.stream1}
            for stream in streams:
                values[stream].extend([{"innse"  : channel.innse,
                                        "outnse" : channel.outnse,
                                        "gain"   : channel.gain}[variable]
                                        for channel in streamDict[stream]])
        
        # Limits on variable values to use for calculating means in order to avoid obviously bad modules
        # NB: This is not trivial at all
        
        for stream in streams:
            values[stream] = np.array(values[stream])
            meanMask = (values[stream] > valueLimits[variable][0]) * (values[stream] < valueLimits[variable][1])
            if len(values[stream][meanMask]) > 0:
                mean = np.mean(np.array(values[stream])[meanMask])
                std = np.std(np.array(values[stream])[meanMask])
            else:
                mean = None
                std = None
            meansDict[subtype][stream] = mean
            stdsDict[subtype][stream] = std
            
            streamDict = {0 : "under", 1 : "away"}
            if showHist:
                plt.hist(values[stream], bins=bins, alpha=0.7,
            label=subtype + "_" + streamDict[stream] + " " + lengthDict[subtype+streamDict[stream]] + " mm" + " (" + str(len(hybrids[subtype])) + " modules)")

    labelDict = {"innse"  : "Input noise [ENC]",
                  "outnse" : "Output noise [mV]",
                  "gain"   : "Gain [mV/fC]"}
    if fig and showHist:
        plt.xlabel(labelDict[variable])
        plt.ylabel("Number of channels")
        plt.legend()
        plt.yscale('log')
        plt.show()

    if len(subtypes) > 1:
        
        if showComp:
            if figsize is None:
                fig = plt.figure()
            else:
                fig = plt.figure(figsize=figsize)
                
        ECMarkers = ['v', '^', '<', '>', '*', 'X', 'D', 'x', '+', '1', '2', '3', '4']
        barrelMarkers = ['o', 's', 'p', 'P']
        markersDict = {}
        ECm = 0
        bm = 0
        for subtype in subtypes:
            if subtype in allBarrelSubtypes:
                markersDict[subtype] = barrelMarkers[bm % len(barrelMarkers)]
                bm += 1
            else:
                markersDict[subtype] = ECMarkers[ECm % len(ECMarkers)]
                ECm += 1
        means = []
        stds = []
        xticks = []
        minLength = 1000
        maxLength = 0
        for s, subtype in enumerate(subtypes):
            for stream in streams:
                if meansDict[subtype][stream] is None:
                    print("No mean value for subtype", subtype, "stream", streamDict[stream])
                else:
                    mean = meansDict[subtype][stream]
                    std = stdsDict[subtype][stream]
                    x = float(lengthDict[subtype+streamDict[stream]])
                    minLength = min(x, minLength)
                    maxLength = max(x, maxLength)
                    print(subtype, "stream", stream, "mean:", mean)
                    
                    if subtype in allSubtypes:
                        means.append(mean)
                        stds.append(std)
                        xticks.append(x)
                    if showComp:
                        plt.errorbar(x, mean, std, marker=markersDict[subtype], markersize=10, elinewidth=2, capsize=10,
                                label=subtype+" "+streamDict[stream]+" "+lengthDict[subtype+streamDict[stream]]+" cm")
        
        fit = True
        if fit:
            from scipy.optimize import curve_fit
            
            def linearFunc(x, intercept, slope):
                return slope*x + intercept
                     
            #slope, intercept, r_value, p_value, std_err = stats.linregress(xticks, means)
            fitParams, cov = curve_fit(linearFunc, xticks, means, sigma=stds, absolute_sigma=True)
            
            intercept = fitParams[0]
            slope = fitParams[1]
            
            print("Fit parameters; slope:", slope, "\nintercept:", intercept)
            
            if showComp:
                x = np.linspace(0, maxLength+0.2, 100)
                #x = np.linspace(minLength-0.2, maxLength+0.2, 100)
                y = slope * x + intercept
                plt.plot(x, y, ":", color="k", label="Linear fit")
                #plt.fill_between(x, slope*x+intercept-std_err, slope*x+intercept+std_err, color="k", alpha=0.2, label="Linear fit sigma")
                #plt.fill_between(x, slope*x+intercept-2*std_err, slope*x+intercept+2*std_err, color="k", alpha=0.15, label="Linear fit 2 sigma")
                #plt.fill_between(x, slope*x+intercept-3*std_err, slope*x+intercept+3*std_err, color="k", alpha=0.1, label="Linear fit 3 sigma")
            
                plt.xlabel('Strip length [cm]')
                plt.ylabel(labelDict[variable])
                plt.title('Hybrid properties vs strip length comparison')
                plt.legend(loc='upper left')
                plt.grid()
                plt.show()

if __name__ == "__main__":

    argv = sys.argv
    filenames = []
    
    if len(argv) < 2:
        filenames = input("Please enter subtype(s) OR filename(s) of json with test IDs (separated with a space): ")
        ECStripLengthNoiseComparison(filenames)
        sys.exit(1)
    else:
        if argv[1] == "all" or argv[1] == "ALL":
            
            with open("../Helpers/subtypes.txt", 'r') as f:
                filenames.extend(f.read().split(','))
            filenames.extend(["SSX", "SSY", "LSX", "LSY"])
        elif argv[1] == "ec" or argv == "EC":
            with open("../Helpers/subtypes.txt", 'r') as f:
                filenames.extend(f.read().split(','))
        else:
            filenames = sys.argv[1:]
        
            
    ECStripLengthNoiseComparison(*filenames)

