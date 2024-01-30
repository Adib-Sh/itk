import matplotlib.pyplot as plt

import sys
sys.path.append("../../../")
from parsers.RCparsers import *
from plots.ResponseCurvePlots import *

datapath = "../../../data/"

instituteColors = {'BNL':'#105c78', 'IFIC':'#f5d979', 'Toronto':'#002a5c'}
glueColors = {'Polaris':"#ff0000", 'TrueBlue':"#0000ff", 'FalseBlue':'#5500ff', 'UnknownGlue':"#000000"}
moduleTypeColors = {'LS': 'lightgrey', 'SS':'grey', 'R0':'green','R1':'gold','R2':'blue','R3':'red','R4':'purple','R5':'orange'}

#File with test names | module type | insitute | gluetype | 
from metadata import loadFileCollections

filecollections = loadFileCollections()

"""
OPTIONS
"""

commentOfInterest = "HIGH NOISE"

#moduletypes = ["R3H0","R3H1","R3H2","R3H3"]
#moduletypes = ["R5H0","R5H1"]
moduletypes = ["LS"]

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

            chipsum = 0
            for i in range(0,len(tests[cyclenum].chips)):
                chipsum += tests[cyclenum].chips[i].meanInnse()

            x.append(cyclenum)
            y.append(chipsum/len(tests[cyclenum].chips))

        ax.plot(x,y,color=instituteColors[collection[3]])  
        
plt.ylabel("# of " + commentOfInterest + "channels")
plt.xlabel("Cycle Number")
plt.title("Thermal cycles of " + str(moduletypes))
#Create legend without duplicates
for institute in set([x[3] for x in filecollections if x[2] in moduletypes]):
    plt.plot([],[],label=institute, color=instituteColors[institute])
plt.legend()
plt.savefig("bwPlot.png")

"""
Plot institute comparisons
"""

"""
Plot glue comparisons
"""


