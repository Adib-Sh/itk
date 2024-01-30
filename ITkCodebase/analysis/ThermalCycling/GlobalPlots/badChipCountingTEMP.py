import matplotlib.pyplot as plt

import sys
sys.path.append("../../../")
from parsers.RCparsers import *
from plots.ResponseCurvePlots import *

datapath = "../../../data/"

instituteColors = {'BNL':'#105c78', 'IFIC':'#f5d979', 'Toronto':'#002a5c'}
glueColors = {'Polaris':"#ff0000", 'TrueBlue':"#0000ff", 'FalseBlue':'#5500ff', 'UnknownGlue':"#000000"}
moduleTypeColors = {'LS': 'lightgrey', 'SS':'grey', 'R0H0':'green', 'R0H1':'green','R1H0':'gold','R1H1':'gold','R2H0':'blue','R2H1':'blue','R3H0':'red','R3H1':'red','R3H2':'red','R3H3':'red','R4H0':'purple','R4H1':'purple','R5H0':'orange', 'R5H1':'orange'}

#File with test names | module type | insitute | gluetype | 
from metadata import loadFileCollections
filecollections = loadFileCollections()

"""
OPTIONS
"""

commentOfInterest = "HIGH NOISE"

#moduletypes = ["R3H0","R3H1","R3H2","R3H3"]
#moduletypes = ["R3H0"]
moduletypes = ["LS","R3H0","R3H1","R3H2","R3H3","R5H0","R5H1"]

read_stream0 = True
read_stream1 = True

#filters?

"""
Plot b-w plot without grouping modules
"""

fig = plt.figure()
ax = fig.gca()

for collection in filecollections:
    if collection[2] in moduletypes:

        tests = []
        
        collectionfile = open(collection[0])
        for f in collectionfile:
            testfilepath = datapath+collection[1]+"/"+f[:-1]
            print(testfilepath)
            tests.append(parseJsonRC(testfilepath,readstream0=read_stream0, readstream1=read_stream1))

        x = []
        y = []

        for cyclenum in range(0,len(tests)):
            noisycounter = 0
            #print(hybridnum)
            tests[cyclenum].classification(strategy="Full")

            if tests[cyclenum].badModule:
                noisycounter += 1
            """
            for i in range(0,len(tests[cyclenum].chips)):
                if tests[cyclenum].chips[i].badchip:
                    noisycounter += 1
            """

            x.append(cyclenum)
            y.append(noisycounter)

        #ax.plot(x,y,color=instituteColors[collection[3]])  
        ax.plot(x,y,color=moduleTypeColors[collection[2]])  
        
#plt.ylabel("# of bad chips")
plt.ylabel("Bad Module")
plt.xlabel("Cycle Number")
plt.title("Thermal cycles of " + str(moduletypes))
#Create legend without duplicates
#for institute in set([x[3] for x in filecollections if x[2] in moduletypes]):
#    plt.plot([],[],label=institute, color=instituteColors[institute])
for moduletype in set([x[2] for x in filecollections]):
    plt.plot([],[],label=moduletype, color=moduleTypeColors[moduletype])
plt.legend()
plt.savefig("bwPlot.png")

"""
Plot institute comparisons
"""

"""
Plot glue comparisons
"""

test = parseJsonRC("../../../data/GroupG/SN20USEH50000036_R3H0_20230626_1264_102_RESPONSE_CURVE_PPA.json",readstream0=read_stream0, readstream1=read_stream1)
test.classification(strategy="Full")

fig = plotRCClassified(test, variable="innse", showStream0=read_stream0, showStream1=read_stream1)
plt.savefig("spectrum.png")
