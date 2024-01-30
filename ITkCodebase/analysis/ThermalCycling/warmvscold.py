"""

"""

import sys
sys.path.append("../../")
from parsers.RCparsers import *
from plots.ResponseCurvePlots import *

import json
from os.path import exists


file = open("PPA_SS.json")
filelist = json.load(file)

#Cold noise in stream 0
read_stream0 = True
read_stream1 = True

"""
Data parsing and filtering
"""
datapath = "../../data/"

print("Parsing room temperature module")
warm_hybrids = []

#Parse loose local files
for filename in list(filelist["warm_filenames"]):
    print(datapath+filename)
    warm_hybrids.append(parseTxtRC(datapath+filename, readstream0=read_stream0, readstream1=read_stream1))


print("Parsing cold modules")
cold_hybrids = []

for filename in list(filelist["cold_filenames"]):
    cold_hybrids.append(parseTxtRC(datapath+filename,readstream0=read_stream0, readstream1=read_stream1))

binMax = 15
binMin = 0
n_bins = 100
bins = np.linspace(binMin, binMax, n_bins)
#plotRCOutnseHistograms(warm_hybrids)
#plotRCUnbondedClassificationOutnseHistograms(warm_hybrids, cold_hybrids, "log", bins=bins, title="R0H0")

hybridnum = 0

warmvariable = []
warm_hybrids[hybridnum].classification(strategy="NathanR0Revised")
for i in range(0,len(warm_hybrids[hybridnum].chips)):
    for channel in warm_hybrids[hybridnum].chips[i].channels:
        if not channel.badchannel:
            warmvariable.append(channel.innse)
    print(warm_hybrids[hybridnum].chips[i].meanOutnse())
#fig = plotRCClassified(warm_hybrids[hybridnum], variable="outnse", showStream0=read_stream0, showStream1=read_stream1)
#plt.show()

coldvariable = []
cold_hybrids[hybridnum].classification(strategy="NathanR0Revised")
for i in range(0,len(cold_hybrids[hybridnum].chips)):
    print(cold_hybrids[hybridnum].chips[i].meanOutnse())
    for channel in cold_hybrids[hybridnum].chips[i].channels:
        if not channel.badchannel:
            coldvariable.append(channel.innse)
#fig = plotRCClassified(cold_hybrids[hybridnum], variable="outnse", showStream0=read_stream0, showStream1=read_stream1)
#plt.show()

plt.hist(warmvariable,histtype="step", label="+18 C")
plt.hist(coldvariable,histtype="step", label="-40 C")
plt.xlabel("Gain")
plt.ylabel("# of channels")
plt.legend()
plt.show()

