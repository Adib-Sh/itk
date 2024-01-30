"""

"""

import sys
sys.path.append("../../../")
from parsers.RCparsers import *
from plots.ResponseCurvePlots import *

import json
from os.path import exists

import mplhep as hep
plt.style.use(hep.style.ATLAS)

datapath = "../../../data/CycleToDeath/" 
filename = "SCIPP-PPB_LS-016.json"

file = open(filename)
filelist = json.load(file)

#Cold noise in stream 0
read_stream0 = True
read_stream1 = True

"""
Data parsing and filtering
"""

print("Parsing room temperature module")
warm_hybrids = []

#Parse loose local files
for f in list(filelist["warm_filenames"]):
    print(datapath+f)
    warm_hybrids.append(parseJsonRC(datapath+f, readstream0=read_stream0, readstream1=read_stream1))

print("Parsing cold modules")
cold_hybrids = []

for f in list(filelist["cold_filenames"]):
    print(len(cold_hybrids))
    cold_hybrids.append(parseTxtRC(datapath+f,readstream0=read_stream0, readstream1=read_stream1))
    print(f)

binMax = 1000
binMin = 750
n_bins = 125
bins = np.linspace(binMin, binMax, n_bins)
#plotRCOutnseHistograms(warm_hybrids)
#plotRCUnbondedClassificationOutnseHistograms(warm_hybrids, cold_hybrids, "log", bins=bins, title="R0H0")

channelcomments = [[] for x in range(0,1280+2*128)]

chipmean = []
chipmeanwarm = []

# Read which "cycles" we want to process (since the .json includes warm tests unfortunately as well)
hybridnumlistfile = open("SCIPP-PPB_LS-016_coldRC.txt")


hybridnums = []
warmhybridnums = []

for line in hybridnumlistfile:
    hybridnums.append(line.split()[0])
    warmhybridnums.append(line.split()[1])

#for hybridnum in range(0,len(cold_hybrids)):
for c, h in enumerate(hybridnums):


    cyclenum = c + 4 #SCIPP modules were tested four times before
    print("cyclenum " + str(cyclenum))
    if h == 'NONE':
        continue
    hybridnum = int(h)
    print("hybridnum " + str(hybridnum))
    
    badchannels = 0
    numchannels = 0

    coldvariable = []
    #cold_hybrids[hybridnum].classification(strategy="JacobChipSigma")
    cold_hybrids[hybridnum].classification(strategy="Full")
    #chipmean.append([int(filelist["cold_filenames_nominal"][hybridnum].split("_")[-1].split(".")[0]), np.mean([cold_hybrids[hybridnum].chips[i].meanInnse() for i in range(0,len(cold_hybrids[hybridnum].chips))]), int(filelist["cold_filenames_nominal"][hybridnum].split("_")[-2])])

    means = []

    print(hybridnum)
    for i in range(0,len(cold_hybrids[hybridnum].chips)):
        print(len(cold_hybrids[hybridnum].chips))
        chipmean.append([cyclenum, cold_hybrids[hybridnum].chips[i].meanInnse()])
        #chipmean.append([cyclenum, cold_hybrids[hybridnum].chips[i].meanGain()])
        #chipmean.append([cyclenum, cold_hybrids[hybridnum].chips[i].meanOutnse()])
        #means.append(cold_hybrids[hybridnum].chips[i].meanOutnse())
        #means.append(cold_hybrids[hybridnum].chips[i].meanGain())
        for k,channel in enumerate(cold_hybrids[hybridnum].chips[i].channels):
            numchannels += 1
            
            if not channel.badchannel:
                coldvariable.append(channel.innse)
            else:
                badchannels += 1
            #print(channel.comment)
            if channel.comment != None:
                channelcomments[128*i+k].append((hybridnum,channel.comment, channel.innse, channel.gain, channel.outnse, channel.channelnumber))
            else:
                channelcomments[128*i+k].append((hybridnum,"", channel.innse, channel.gain, channel.outnse, channel.channelnumber))
      
    #fig = plotRCClassified(cold_hybrids[hybridnum], variable="outnse", showStream0=read_stream0, showStream1=read_stream1)
    #plt.show()
    #chipmean.append([cyclenum, sum(means)/float(len(means))])



    #plt.hist(warmvariable,histtype="step", label="Warm")
    #plt.hist(coldvariable,histtype="step", bins=bins,label="Cold cycle "+str(hybridnum))

    outnse_rms = [x.meanOutnse() for x in cold_hybrids[hybridnum].chips ]
    #plt.scatter([hybridnum for x in cold_hybrids[hybridnum].chips], outnse_rms)

    #plt.scatter(hybridnum, badchannels)
#plt.show()

#for hybridnum in [0,1,2,3,4,5,6,7,8,9,10]:
#for hybridnum in []:
for c,h in enumerate(warmhybridnums):
    
    cyclenum = c + 4 #SCIPP modules were tested four times before
    print("cyclenum " + str(cyclenum))
    if h == 'NONE':
        continue
    hybridnum = int(h)
    print("hybridnum " + str(hybridnum))
    
    badchannels = 0
    numchannels = 0

    coldvariable = []
    #cold_hybrids[hybridnum].classification(strategy="JacobChipSigma")
    #warm_hybrids[hybridnum].classification(strategy="Full")
    for i in range(0,len(cold_hybrids[hybridnum].chips)):
        print(len(cold_hybrids[hybridnum].chips))
        chipmeanwarm.append([cyclenum, cold_hybrids[hybridnum].chips[i].meanInnse()])
        #chipmeanwarm.append([cyclenum, cold_hybrids[hybridnum].chips[i].meanGain()])
        #chipmeanwarm.append([cyclenum, cold_hybrids[hybridnum].chips[i].meanOutnse()])
        #for k,channel in enumerate(cold_hybrids[hybridnum].chips[i].channels):
            #numchannels += 1
            #
            #if not channel.badchannel:
            #    coldvariable.append(channel.innse)
            #else:
            #    badchannels += 1
            #print(channel.comment)
            #if channel.comment != None:
            #    channelcomments[128*i+k].append((hybridnum,channel.comment, channel.innse, channel.gain, channel.outnse, channel.channelnumber))
            #else:
            #    channelcomments[128*i+k].append((hybridnum,"", channel.innse, channel.gain, channel.outnse, channel.channelnumber))
      
    #fig = plotRCClassified(cold_hybrids[hybridnum], variable="outnse", showStream0=read_stream0, showStream1=read_stream1)
    #plt.show()

    #plt.hist(warmvariable,histtype="step", label="Warm")
    #plt.hist(coldvariable,histtype="step", bins=bins,label="Cold cycle "+str(hybridnum))

    #outnse_rms = [x.meanOutnse() for x in cold_hybrids[hybridnum].chips ]

ymin = 800
ymax = 1200

may18lines = [74.5+4, 81.5+4]

#strangetests = [159,179,211,221,239,245,247,311,331,335,339,225,261]
#strangecoldstrobes = [211,225,261]
#plt.vlines(strangetests,ymin,ymax,color="black",linestyle="dashed")
#plt.vlines(may18lines,ymin,ymax,color="black",linestyle="dashed")
#plt.vlines(strangecoldstrobes,ymin,ymax,color="black",linestyle="dashed")

plt.scatter([x[0] for x in chipmean], [x[1] for x in chipmean], label="Cold")
plt.scatter([x[0] for x in chipmeanwarm], [x[1] for x in chipmeanwarm], label="Warm")

plt.ylim(ymin,ymax)

hep.atlas.text("ITk Internal")
plt.xlabel("Cycle # ")
plt.ylabel("Chip mean input noise")
plt.legend()
plt.title(filename)
plt.show()

#for i in range(0,1280):
#    if len(channelcomments[i]) > 0:
#        print(i)
#        print(channelcomments[i])

"""
points = []
for i in range(0,400):
    count = 0
    for j,x in enumerate(channelcomments):
        for k in x:
            if k[0] == i and "HIGH NOISE" in k[1] :
                count += 1
                plt.scatter(j, i,color="black",s=5)
    #plt.scatter(i,count)
    points.append(count)
#plt.plot(range(0,11),points)
plt.xlabel("Channel number (?) on away side")
plt.ylabel("Thermal Cycle")
plt.title(filename)
plt.show()
print(points)

plt.plot(range(0,400),points)
plt.xlabel("Cold cycle")
plt.ylabel("# of HIGH NOISE channels")
plt.show()
"""
noisyvariance = []
normalvariance = []

noisyvarianceoutnse = []
normalvarianceoutnse = []

highgainvariance = []
normalgainvariance = []

"""
for j,x in enumerate(channelcomments):
    highnoise = False
    highgain = False
    for k in x:
        if "HIGH NOISE" in k[1]:
            highnoise = True
        if "HIGH GAIN" in k[1]:
            #print(k)
            highgain = True

    mean = 0
    for k in x:
        mean += k[2]
    mean = mean / len(x)
    
    meanoutnse = 0
    for k in x:
        meanoutnse += k[4]
    meanoutnse = meanoutnse / len(x)
    
    meangain = 0
    for k in x:
        meangain += k[3]
    meangain = meangain / len(x)

    #print("meangain " + str(meangain))

    variance = 0
    for k in x:
        variance += (k[2]-mean)**2
    variance = variance / len(x)
    
    varianceoutnse = 0
    for k in x:
        varianceoutnse += (k[4]-meanoutnse)**2
    varianceoutnse = varianceoutnse / len(x)
    
    #print("varianceoutnse " + str(varianceoutnse))
    
    variancegain = 0
    for k in x:
        variancegain += (k[3]-meangain)**2
    variancegain = variancegain / len(x)
    #print("variancegain " + str(variancegain))
    
    if highnoise:
        noisyvariance.append(variance)
    else:
        normalvariance.append(variance)
    
    if highnoise:
        noisyvarianceoutnse.append(varianceoutnse)
    else:
        normalvarianceoutnse.append(varianceoutnse)

    #if varianceoutnse > 0.2:
    print(j)
    print(x)

    if highgain:
        highgainvariance.append(variancegain)
    else:
        normalgainvariance.append(variancegain)

bins = np.linspace(0,35,100)
#plt.hist(noisyvariance, bins=bins, histtype="step", label="HIGH NOISE", density=True)
#plt.hist(normalvariance, bins=bins, histtype="step", label="Not HIGH NOISE", density=True)
plt.hist(noisyvarianceoutnse, bins=bins, histtype="step", label="HIGH NOISE (at least once)", density=True)
plt.hist(normalvarianceoutnse, bins=bins, histtype="step", label="Not HIGH NOISE", density=True)
#plt.hist(highgainvariance, bins=bins, histtype="step", label="HIGH NOISE", density=True)
#plt.hist(normalgainvariance, bins=bins, histtype="step", label="Not HIGH NOISE", density=True)
plt.legend()
plt.xlabel("Output noise variance between cold cycles")
plt.title("BNL-PPB2-MLS-112, 2.5 sigma cut")
plt.show()
"""

#fig = plotRCClassified(cold_hybrids[281], variable="gain", showStream0=read_stream0, showStream1=read_stream1)
#fig = plotRCClassified(cold_hybrids[283], variable="gain", showStream0=read_stream0, showStream1=read_stream1)

fig = plotRCClassified(cold_hybrids[305], variable="innse", showStream0=read_stream0, showStream1=read_stream1)
fig = plotRCClassified(cold_hybrids[407], variable="innse", showStream0=read_stream0, showStream1=read_stream1)

#plt.xlabel("Gain")
#plt.ylabel("# of channels")
#plt.legend()
plt.show()


