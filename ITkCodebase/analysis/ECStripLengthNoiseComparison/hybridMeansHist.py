import numpy as np
import matplotlib.pyplot as plt
from barrelData import getBarrelHybrids
from Helpers.getHybridsFromIDFile import *

def main(subtype, variable="innse"):

    allBarrelSubtypes = ["SSX", "SSY", "LSX", "LSY"]
    with open("../Helpers/subtypes.txt", 'r') as f:
        allECSubtypes = f.read().split(',')
        allSubtypes = []
        allSubtypes.extend(allECSubtypes)
        allSubtypes.extend(allBarrelSubtypes)

    if subtype in allBarrelSubtypes:
        hybrids = getBarrelHybrids(subtype)
    if subtype in allECSubtypes:
        unbonded_hybrids, hybrids = getHybridsFromIDFile(subtype + "data.json")

    print("Number of", subtype, "subtypes:", len(hybrids))
    print("Variable", variable)

    means = []

    for hybrid in hybrids:
        mean = np.mean([{"innse"  : channel.innse,
                        "outnse" : channel.outnse,
                        "gain"   : channel.gain}[variable]
                        for channel in hybrid.getStream(0)])
        #if mean < 2000:
        means.append(mean)
        print(means[-1])
        
    plt.hist(means, bins=60)
    plt.show()

if __name__ == "__main__":
    import sys
    argv = sys.argv
    if len(argv) < 2:
        print("Please specify subtype. Aborting.")
        sys.exit(0)
    subtype = argv[1]
    if len(argv) == 2:
        variable = "innse"
    else:
        variable = argv[2]
    main(subtype, variable)