cutsDict = {'R0H0' : [0.1, 11],
 'R0H1' : [0.1, 12],
 'R1H0' : [0.1, 11],
 'R1H1' : [0.1, 10],
 'R2H0' : [0.1, 13],
 'R2H1' : [0.1, 13],
 'R3H0' : [0.1, 15],
 'R3H1' : [0.1, 15],
 'R3H2' : [0.1, 15],
 'R3H3' : [0.1, 15],
 'R4H0' : [0.1, 15],
 'R4H1' : [0.1, 15],
 'R5H0' : [0.1, 15],
 'R5H1' : [0.1, 15]}

def getCutsDict():
    return cutsDict

def getCuts(subtype):
    return cutsDict[subtype]