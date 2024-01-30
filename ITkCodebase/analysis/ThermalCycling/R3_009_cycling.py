"""

"""

import sys
sys.path.append("../../")
from parsers.RCparsers import *
from plots.ResponseCurvePlots import *

import json
from os.path import exists


file = open("PPA_R3_009.json")
filelist = json.load(file)

#Cold noise in stream 0
read_stream0 = True
read_stream1 = True

"""
Data parsing and filtering
"""
datapath = "../../data/PPA_EC/"

print("Parsing room temperature module")
warm_hybrids = []

#Parse loose local files
for filename in list(filelist["warm_filenames"]):
    print(datapath+filename)
    warm_hybrids.append(parseTxtRC(datapath+filename, readstream0=read_stream0, readstream1=read_stream1))


print("Parsing cold modules")
cycle0_hybrids = []

for filename in list(filelist["cycle0_filenames"]):
    cycle0_hybrids.append(parseTxtRC(datapath+filename,readstream0=read_stream0, readstream1=read_stream1))

cycle1_hybrids = []

for filename in list(filelist["cycle1_filenames"]):
    cycle1_hybrids.append(parseTxtRC(datapath+filename,readstream0=read_stream0, readstream1=read_stream1))

cycle2_hybrids = []

for filename in list(filelist["cycle2_filenames"]):
    cycle2_hybrids.append(parseTxtRC(datapath+filename,readstream0=read_stream0, readstream1=read_stream1))


binMax = 15
binMin = 0
n_bins = 100
bins = np.linspace(binMin, binMax, n_bins)
#plotRCOutnseHistograms(cycle0_hybrids)
#plotRCUnbondedClassificationOutnseHistograms(cycle0_hybrids, cycle1_hybrids, "log", bins=bins, title="R0H0")

hybridnum = 3

cycle0 = []
cycle1 = []
cycle2 = []

print("CYCLE 0")
cycle0_hybrids[hybridnum].classification(strategy="NathanR0Revised")
for i in range(0,len(cycle0_hybrids[hybridnum].chips)):
    print(cycle0_hybrids[hybridnum].chips[i].meanOutnse())
    cycle0.append(cycle0_hybrids[hybridnum].chips[i].meanInnse())
fig = plotRCClassified(cycle0_hybrids[hybridnum], variable="gain", showStream0=read_stream0, showStream1=read_stream1)
plt.show()

print("CYCLE 1")
cycle1_hybrids[hybridnum].classification(strategy="NathanR0Revised")
for i in range(0,len(cycle1_hybrids[hybridnum].chips)):
    print(cycle1_hybrids[hybridnum].chips[i].meanOutnse())
    cycle1.append(cycle1_hybrids[hybridnum].chips[i].meanInnse())
fig = plotRCClassified(cycle1_hybrids[hybridnum], variable="gain", showStream0=read_stream0, showStream1=read_stream1)
plt.show()

print("CYCLE 2")
cycle2_hybrids[hybridnum].classification(strategy="NathanR0Revised")
for i in range(0,len(cycle2_hybrids[hybridnum].chips)):
    print(cycle2_hybrids[hybridnum].chips[i].meanOutnse())
    cycle2.append(cycle2_hybrids[hybridnum].chips[i].meanInnse())
fig = plotRCClassified(cycle2_hybrids[hybridnum], variable="gain", showStream0=read_stream0, showStream1=read_stream1)
plt.show()

#plt.scatter([0 for x in cycle0], cycle0)
#plt.scatter([1 for x in cycle1], cycle1)
#plt.scatter([2 for x in cycle2], cycle2)

#plt.xticks([0,1,2])
#plt.xlabel("Cold cycle")
#plt.ylabel("Mean Input Noise")
#plt.title("Toronto R3H"+str(hybridnum)+" at -40 degrees C, stream0="+str(read_stream0)+" stream1="+str(read_stream1))

#plt.show()
