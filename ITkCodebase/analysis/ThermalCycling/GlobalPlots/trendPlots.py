"""


Author: Erik Wallin
"""

import matplotlib.pyplot as plt

import sys
sys.path.append("../../../")
from parsers.RCparsers import *
from plots.ResponseCurvePlots import *

datapath = "../../../data/"

instituteColors = {'BNL':'#105c78', 'IFIC':'#f5d979', 'Toronto':'#002a5c', 'SCIPP':"#ff0000", 'CAM':"#fee56e"}
glueColors = {'Polaris':"#ff0000", 'TrueBlue':"#0000ff", 'FalseBlue':'#5500ff', 'UnknownGlue':"#000000"}
moduleTypeColors = {'LS': 'lightgrey', 'SS':'grey', 'R0H0':'green', 'R0H1':'green','R1H0':'gold','R1H1':'gold','R2H0':'blue','R2H1':'blue','R3H0':'red','R3H1':'red','R3H2':'red','R3H3':'red','R4H0':'purple','R4H1':'purple','R5H0':'orange', 'R5H1':'orange'}

#File with test names | module type | insitute | gluetype | 
from metadata import loadFileCollections
filecollections = loadFileCollections()

"""
OPTIONS
"""

"""
plot types: "commentCounting", "variableAverage", "variableSigma"
"""
plotType = "variableAverage"

#For plot type "commentCounting", choose comment:
commentOfInterest = "HIGH NOISE"

#For plot types "variableAverage" and "variableSigma", possible variables to plot are: innse, outnse, gain, offset
variableOfInterest = "outnse"

plotAverage = True

#moduletypes = ["R3H0","R3H1","R3H2","R3H3"]
#moduletypes = ["R5H0","R5H1"]
#moduletypes = ["LS","R3H0","R3H1","R3H2","R3H3","R5H0","R5H1"]
moduletypes = ["LS"]

read_stream0 = True
read_stream1 = True

"""
Label grouping, options: moduleType, institute, moduleSN

"moduleSN" can possibly make the legend very long
"""
groupBy = "institute"

"""
FILTERS
"""

#Plot modules that failed or passed cycling
plotFailedCycling = True
plotPassedCycling = False

#Minimum number of cycles?

"""
HISTOGRAM OPTIONS
"""

"""
Plotting
"""

fig = plt.figure()
ax = fig.gca()

#Save all trend lines for computing an average later
allY = []

for collection in filecollections:
    if collection[2] in moduletypes:

        passedCycling = True

        tests = []
        
        collectionfile = open(collection[0])
        for f in collectionfile:
            testfilepath = datapath+collection[1]+"/"+f[:-1]
            print(testfilepath)
            tests.append(parseJsonRC(testfilepath,readstream0=read_stream0, readstream1=read_stream1))

        x = []
        y = []

        histogramEntries = []

        for cyclenum in range(0,len(tests)):
            tests[cyclenum].classification(strategy="Full")
            if tests[cyclenum].badModule == True:
                passedCycling = False

            if plotType == "commentCounting":
                noisycounter = 0
                #print(hybridnum)
                #tests[cyclenum].classification(strategy="Full")

                for i in range(0,len(tests[cyclenum].chips)):
                    for k,channel in enumerate(tests[cyclenum].chips[i].channels):
                        #print(channel.comment)
                        if commentOfInterest in channel.comment:
                            noisycounter += 1

                x.append(cyclenum)
                y.append(noisycounter)

            if plotType == "variableAverage":
                s = 0

                #tests[cyclenum].classification(strategy="Full")

                for i in range(0,len(tests[cyclenum].chips)):
                    if variableOfInterest == "innse":
                        s += tests[cyclenum].chips[i].meanInnse()
                    if variableOfInterest == "outnse":
                        s += tests[cyclenum].chips[i].meanOutnse()
                    if variableOfInterest == "gain":
                        s += tests[cyclenum].chips[i].meanGain()

                x.append(cyclenum)
                y.append(s/len(tests[cyclenum].chips))
            
            if plotType == "variableSigma":
                s = 0

                for i in range(0,len(tests[cyclenum].chips)):
                    if variableOfInterest == "innse":
                        s += tests[cyclenum].chips[i].sigmaInnse()
                    if variableOfInterest == "outnse":
                        s += tests[cyclenum].chips[i].sigmaOutnse()
                    if variableOfInterest == "gain":
                        s += tests[cyclenum].chips[i].sigmaGain()
                
                x.append(cyclenum)
                y.append(s/len(tests[cyclenum].chips))
                
        if len(x) > 0 and ((passedCycling and plotPassedCycling) or ((not passedCycling) and plotFailedCycling)):
            allY.append(y)

            if groupBy == "institute":
                ax.plot(x,y,color=instituteColors[collection[3]])
            elif groupBy == "moduleSN":
                ax.plot(x,y,label=collection[0].split('/')[-1])
            else:
                ax.plot(x,y,color=moduleTypeColors[collection[2]])  

if plotType == "commentCounting":        
    plt.ylabel("# of channels flagged as " + commentOfInterest)
if plotType == "variableAverage":
    if variableOfInterest == "innse":
        plt.ylabel("Mean input noise [ENC]")
    if variableOfInterest == "outnse":
        plt.ylabel("Mean output noise [mV]")
    if variableOfInterest == "gain":
        plt.ylabel("Mean gain [mV/fC]")
if plotType == "variableSigma":
    plt.ylabel("Mean chip " + variableOfInterest + " std. dev.")

if plotAverage:
    averageX = []
    averageY = []
    for x in range(0,max([len(l) for l in allY])):
        s = sum([l[x] for l in allY if len(l) >= x+1])
        averageY.append( s / len([l[x] for l in allY if len(l) >= x+1]))
        averageX.append(x)

    ax.plot(averageX, averageY, linewidth=5, color="black", label="Average")

plt.xlabel("Cycle Number")
plt.title("Thermal cycles of " + str(moduletypes))
#Create legend without duplicates
if groupBy == "institute":
    for institute in set([x[3] for x in filecollections if x[2] in moduletypes]):
        plt.plot([],[],label=institute, color=instituteColors[institute])
elif groupBy == "moduleSN":
    pass
else:
    for moduletype in set([x[2] for x in filecollections]):
        plt.plot([],[],label=moduletype, color=moduleTypeColors[moduletype])
plt.legend()
plt.savefig("bwPlot.png", dpi=300)

