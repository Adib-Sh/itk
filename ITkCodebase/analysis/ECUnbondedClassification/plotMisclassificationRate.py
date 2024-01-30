import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append("../")
from Helpers.getHybridsFromIDFile import getHybridsFromIDFile
from Helpers.getCuts import *

def plotMisclassificationRate(subtype, verbose=False):
    
    filename = "../Helpers/jsonFiles/" + subtype + "data.json"
    
    cuts = getCuts(subtype)
    
    bondStatuses = ["unbonded", "bonded"]
    hybrids = dict(zip(bondStatuses, getHybridsFromIDFile(filename, verbose=verbose)))
    outnses = {"unbonded" : [], "bonded" : []}
    for bondStatus in bondStatuses:
        for hybrid in hybrids[bondStatus]:
            channelDict = {"unbonded" : hybrid.channels,
                           "bonded" : hybrid.getStream(1)}
            outnses[bondStatus].extend([channel.outnse for channel in channelDict[bondStatus]])
        outnses[bondStatus] = np.array(outnses[bondStatus])
        mask = (outnses[bondStatus] > cuts[0]) & (outnses[bondStatus] < cuts[1])
        outnses[bondStatus] = outnses[bondStatus][mask]
        
    abort = False
    for bondStatus in ["unbonded", "bonded"]:
        if len(hybrids[bondStatus]) == 0:
            print("No", bondStatus, "hybrids for subtype", subtype + ". Cannot run misclassification plot.")
            abort = True
    if abort:
        return
        
    binMin = cuts[0]
    binMax = cuts[1]
    nBins = 500
    bins = np.linspace(binMin, binMax, nBins)
    binCounts = {}
    binEdges = {}
    binCenters = {}
    for bondStatus in outnses:
        binCounts[bondStatus], binEdges[bondStatus] = np.histogram(outnses[bondStatus], bins=bins)
        binCenters[bondStatus] = [(binEdges[bondStatus][i] + binEdges[bondStatus][i+1]) / 2 for i in range(len(binEdges[bondStatus])-1)]
    
    from scipy.optimize import curve_fit
    
    mean = {}
    sigma = {}
    popt = {}
    pcov = {}
    for bondStatus in outnses:
        mean[bondStatus] = np.mean(outnses[bondStatus])
        sigma[bondStatus] = np.std(outnses[bondStatus])
        popt[bondStatus], pcov[bondStatus] = curve_fit(Gauss, binCenters[bondStatus],
                                                       binCounts[bondStatus],
                                                       p0=[max(binCounts[bondStatus]),
                                                       mean[bondStatus],
                                                       sigma[bondStatus]])
    def UnbondedGauss(x):
        return Gauss(x, *popt['unbonded'])
    def BondedGauss(x):
        return Gauss(x, *popt['bonded'])

    fig, axs = plt.subplots(2, 1, figsize=(6,10))
    colors = {'unbonded' : 'b', 'bonded' : 'r'}
    for bondStatus in outnses:
        axs[0].hist(outnses[bondStatus], bins=bins, color=colors[bondStatus], alpha=0.3, label=bondStatus)
        axs[0].plot(binCenters[bondStatus], Gauss(binCenters[bondStatus], *popt[bondStatus]), '-', color=colors[bondStatus])
    
    
    histLimits = (mean["unbonded"]+1*sigma["unbonded"], mean["bonded"]-1*sigma["bonded"])
    axs[0].set_xlim(histLimits[0], histLimits[1])
    axs[0].set_ylim(0, 50)
    axs[0].set_ylabel('# channels')
    axs[0].set_xlabel('Output noise')
    axs[0].legend()
    axs[0].set_title("Subtype " + subtype)

    import scipy.integrate as integrate
    
    limits = (mean["unbonded"]+2*sigma["unbonded"], mean["bonded"]-2*sigma["bonded"])
    unbondedCuts = np.linspace(limits[0], limits[1], int((limits[1]-limits[0])*100))
    misRate = {'unbonded' : [],
               'bonded' : []}
    functions = {'unbonded' : UnbondedGauss,
                 'bonded' : BondedGauss}
    for bondStatus in outnses:
        for cut in unbondedCuts:
            under, _ = integrate.quad(functions[bondStatus], 0, cut)
            over, _ = integrate.quad(functions[bondStatus], cut, 10)
            misRate[bondStatus].append(100 * min(under, over) / (over + under))
    
    # Figure out reasonably y limits based on where the intersect between the bonded/unbonded curves lies
    prevDiff = 1000000
    for closestIdx, (unbondedMisRate, bondedMisRate) in enumerate(zip(misRate["unbonded"], misRate["bonded"])):
        diff = np.abs(unbondedMisRate - bondedMisRate)
        if diff > prevDiff:
            closestIdx -= 1
            break
        prevDiff = diff
    
    yHighLimit = bondedMisRate*2
    
    axs[1].plot(unbondedCuts, misRate['unbonded'], '.', color=colors['unbonded'], label='unbonded')
    axs[1].plot(unbondedCuts, misRate['bonded'], '.', color=colors['bonded'], label='bonded')
    axs[1].set_ylabel('Misclassification %')
    axs[1].set_xlabel('Output noise unbonded cut')
    axs[1].set_ylim([0, yHighLimit])
    axs[1].grid(visible=True)
    axs[1].legend()
    axs[1].set_title("Subtype " + subtype)
    
    axs[1].axvline(unbondedCuts[closestIdx], 0, 1, alpha = 0.5, linestyle = "--")
    
    plt.subplots_adjust(hspace=0.3)
    plt.show()
    
def Gauss(x, a, x0, sigma):
    return a * np.exp (-(x - x0)**2 / (2 * sigma**2))

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        subtype = input("Please specify module subtype: ")
    else:
        subtype = argv[1]
    plotMisclassificationRate(subtype)