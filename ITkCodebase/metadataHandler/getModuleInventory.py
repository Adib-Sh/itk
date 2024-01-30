import sys, os
sys.path.append(os.getcwd())
from metadataHandler.resultCollector import collectResults

def getModuleInventory(criteria):
    testTuples = collectResults(criteria)
    testTuples = sorted(testTuples, key=lambda x : x[1]["ModuleSN"])
    #moduleSNs = sorted(set([testTuple[1]["ModuleSN"] for testTuple in testTuples]))
    for testTuples in testTuples:
        print(testTuples[1]["ModuleSN"])
        print(testTuples[1])
        print()

if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        sys.exit("Please give some criteria.")
    
    keywords = args[1::2]
    values = args[2::2]
    criteria = dict(zip(keywords, values))
    getModuleInventory(criteria)
