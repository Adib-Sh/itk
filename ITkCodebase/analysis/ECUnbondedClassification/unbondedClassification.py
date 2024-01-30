"""

"""

import sys
sys.path.append("../../")
sys.path.append("../")
from parsers.RCparsers import *
from plots.ResponseCurvePlots import *

import json
from os.path import exists

from Helpers.getHybridsFromIDFile import *


def unbondedClassification(filename, verbose=True):

    if not exists(filename):
        filename = "../Helpers/jsonFiles/" + filename
    subtype = filename.split("/")[-1][:4]

    unbonded_hybrids, bonded_hybrids = getHybridsFromIDFile(filename, verbose=verbose)

    binMax = 20
    binMin = 0
    n_bins = 100
    bins = np.linspace(binMin, binMax, n_bins)
    
    title = subtype
    
    fig = plotRCUnbondedClassificationOutnseHistograms(unbonded_hybrids, bonded_hybrids, "log", bins=bins, title=title)
    
    return fig



if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "R0H1data.json"
    unbondedClassification(filename)