import sys
sys.path.append("../../")
from parsers.RCparsers import parseRC
import glob
import matplotlib.pyplot as plt
import numpy as np

def getBarrelData(barrelSubtypes, variable="innse"):
    
    if __name__ == "__main__":
        fig = plt.figure()
        bins = np.linspace(0, 1200, 60)

    barrelHybrids = {}    
    means = {}
    values = {}
    for subtype in barrelSubtypes:
        barrelHybrids[subtype] = getBarrelHybrids(subtype)
        values[subtype] = [[], []]
        for hybrid in barrelHybrids[subtype]:
            for stream in [0, 1]:
                values[subtype][stream].extend([{"innse"  : channel.innse,
                                        "outnse" : channel.outnse,
                                        "gain"   : channel.gain}[variable]
                                        for channel in hybrid.getStream(stream)])
        
        means[subtype] = [[], []]
        for stream in [0, 1]:
            values[subtype][stream] = np.array(values[subtype][stream])
            mask = (values[subtype][stream] > 400) & (values[subtype][stream] < 1200)
            means[subtype][stream] = np.mean(values[subtype][stream][mask]) if len(values[subtype][stream][mask]) > 0 else None
            if __name__ == "__main__":
                plt.hist(values[subtype][stream], bins=bins, alpha=0.7, label=subtype+" stream"+str(stream))

    if __name__ == "__main__":
        plt.legend()
        plt.title('Barrel modules')
        plt.xlabel('Input noise [ENC]')
        plt.ylabel('# channels')
        plt.yscale('log')
        plt.show()

    return barrelSubtypes, values, means

def getBarrelHybrids(subtype, verbose=True):
    barrelDataPath = "../../../data/"
    barrelFiles = glob.glob(barrelDataPath + "**/*.txt", recursive=True)

    barrelHybrids = []

    for barrelFile in barrelFiles:
        filename = barrelFile.split('/')[-1]
        if "RC" in filename:
            thisSubtype = None
            if "SS" in filename:
                if "_X_" in filename:
                    thisSubtype = "SSX"
                elif "_Y_" in filename:
                    thisSubtype = "SSY"
            elif "LS" in filename:
                if "_X_" in filename:
                    thisSubtype = "LSX"
                elif "_Y_" in filename:
                    thisSubtype = "LSY"
            
            if thisSubtype == subtype:
                barrelHybrids.append(parseRC(barrelFile, verbose=verbose))

    print("Number of", subtype, "hybrids:", len(barrelHybrids))
    
    return barrelHybrids
    
if __name__ == "__main__":
    barrelSubtypes = ["SSX", "SSY", "LSX", "LSY"]
    _, _, means = getBarrelData(barrelSubtypes)
    print(means)