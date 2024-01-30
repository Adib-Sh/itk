"""

"""

import sys
sys.path.append("../../")
from parsers.RCparsers import *
from plots.ResponseCurvePlots import *

import json
from os.path import exists

filename = "BNL-PPB2-MLS-112.json"
file = open(filename)
filelist = json.load(file)

#Cold noise in stream 0
read_stream0 = False
read_stream1 = True

"""
Data parsing and filtering
"""
datapath = "../../data/Abraham/BNL-PPB2-MLS-112/json/" 

print("Parsing room temperature module")
warm_hybrids = []

#Parse loose local files
for filename in list(filelist["warm_filenames"]):
    print(datapath+filename)
    warm_hybrids.append(parseJsonRC(datapath+filename, readstream0=read_stream0, readstream1=read_stream1))


print("Parsing cold modules")
cold_hybrids = []

for filename in list(filelist["cold_filenames"]):
    cold_hybrids.append(parseJsonRC(datapath+filename,readstream0=read_stream0, readstream1=read_stream1))

binMax = 1000
binMin = 750
n_bins = 125
bins = np.linspace(binMin, binMax, n_bins)
#plotRCOutnseHistograms(warm_hybrids)
#plotRCUnbondedClassificationOutnseHistograms(warm_hybrids, cold_hybrids, "log", bins=bins, title="R0H0")

channelcomments = [[] for x in range(0,1280)]

#for hybridnum in range(0,len(cold_hybrids)):
for hybridnum in [0,1,2,3,4,5,6,7,8,9,10]:
    badchannels = 0
    numchannels = 0

    coldvariable = []
    cold_hybrids[hybridnum].classification(strategy="JacobChipSigma")
    for i in range(0,len(cold_hybrids[hybridnum].chips)):
        for k,channel in enumerate(cold_hybrids[hybridnum].chips[i].channels):
            numchannels += 1
            
            #if not channel.badchannel:
            #    coldvariable.append(channel.innse)
            #else:
            #    badchannels += 1
            print(channel.comment)
            if channel.comment != None:
                channelcomments[128*i+k].append((hybridnum,channel.comment, channel.innse, channel.gain, channel.outnse, channel.channelnumber))
            else:
                channelcomments[128*i+k].append((hybridnum,"", channel.innse, channel.gain, channel.outnse, channel.channelnumber))
      
    #fig = plotRCClassified(cold_hybrids[hybridnum], variable="outnse", showStream0=read_stream0, showStream1=read_stream1)
    #plt.show()

    #plt.hist(warmvariable,histtype="step", label="Warm")
    #plt.hist(coldvariable,histtype="step", bins=bins,label="Cold cycle "+str(hybridnum))

    outnse_rms = [x.meanOutnse() for x in cold_hybrids[hybridnum].chips ]
    #plt.scatter([hybridnum for x in cold_hybrids[hybridnum].chips], outnse_rms)

    #plt.scatter(hybridnum, badchannels)
#plt.show()

#for i in range(0,1280):
#    if len(channelcomments[i]) > 0:
#        print(i)
#        print(channelcomments[i])


"""
points = []
for i in range(0,11):
    count = 0
    for j,x in enumerate(channelcomments):
        for k in x:
            if k[0] == i and "HIGH NOISE" in k[1] :
                count += 1
                plt.scatter(j, i,color="black",s=5)
    #plt.scatter(i,count)
    points.append(count)
plt.xlabel("Channel number (?) on away side")
plt.ylabel("Thermal Cycle")
plt.title(filename)
plt.show()
print(points)
"""

goodmean = []
badmean = []

countunbonded = [0 for x in range(0,11)]
counthighnoise = [0 for x in range(0,11)]
counthighgain = [0 for x in range(0,11)]

for j,x in enumerate(channelcomments):
    X = []
    Y = []
    channelnumber = -1

    noisy = False

    for i,k in enumerate(x):
        #if "HIGH NOISE" in k[1]:
        #print(k[1])
        if "HIGH NOISE" in k[1]:
            counthighnoise[i] += 1
            noisy = True
        if "HIGH GAIN" in k[1]:
            counthighgain[i] += 1
        if "LOW NOISE (UNBONDED)" in k[1]:
            countunbonded[i] += 1

    means = [0 for _ in range(0,11)]
    for i,k in enumerate(x):
        #if "HIGH NOISE" in k[1]:
        #if noisy == True:
        if "HIGH NOISE" in k[1]:
            X.append(i)
            Y.append(k[2])
            channelnumber = k[5]
            means[i] += k[3]
        else:
            means[i] += k[3]

    #print(means)

    if noisy:
        badmean.append(means)
    else:
        goodmean.append(means)

    print(X)
    print(Y)
    #if noisy == True:
    if len(Y) > 0:
        if max(Y) > 930:
            #if abs(Y[-1]-Y[0]) > 0.75:
            plt.plot(X,Y, marker="*", label=channelnumber)

plt.xlabel("Cycle #")
plt.ylabel("Input Noise")
plt.title("BNL-PPB2-MLS-112.json")
#plt.legend()

#print(counthighnoise)

plt.show()

bins=np.linspace(0,20,100)
plt.hist([x[0] for x in goodmean], histtype="step", bins=bins, label="Cycle 0")
plt.hist([x[1] for x in goodmean], histtype="step", bins=bins, label="Cycle 1")
plt.hist([x[10] for x in goodmean], histtype="step", bins=bins, label="Cycle 10")
plt.legend()
#plt.hist(badmean)
plt.xlabel("Input Noise")
plt.ylabel("# of Channels")
plt.title("Non-HIGH NOISE channels only, BNL-PPB2-MLS-113")
plt.show()

"""
noisyvariance = []
normalvariance = []

noisyvarianceoutnse = []
normalvarianceoutnse = []

highgainvariance = []
normalgainvariance = []

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

fig = plotRCClassified(cold_hybrids[0], variable="gain", showStream0=read_stream0, showStream1=read_stream1)
fig = plotRCClassified(cold_hybrids[7], variable="gain", showStream0=read_stream0, showStream1=read_stream1)

plt.xlabel("Gain")
plt.ylabel("# of channels")
plt.legend()
plt.show()
"""

