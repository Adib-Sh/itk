import json
import sys
sys.path.append("../")
from Helpers.getECSubtypes import getECSubtypes
from Helpers.getHybridsFromIDFile import getHybridsFromIDFile

class FeatureLibrary:
    def __init__(self, libraryPath, IDDataPath, testPath, allSubtypes):
        self.libraryPath = libraryPath
        if self.libraryPath[-1] != "/":
            self.libraryPath += "/"
        self.IDDataPath = IDDataPath
        self.testPath = testPath
        self.allSubtypes = allSubtypes
        
        self.featureDict = {}

        for subtype in allSubtypes:
            filename = libraryPath + subtype + "FeatureDict.json"
            with open(filename, "r") as f:
                self.featureDict[subtype] = json.load(f)
            
        self.featureCount = {}
        for key in self.featureDict:
            for ID in self.featureDict[key]:
                theseFeatures = self.featureDict[key][ID]
                for feature in theseFeatures:
                    if not feature in self.featureCount.keys():
                        self.featureCount[feature] = 0
                    self.featureCount[feature] += 1
        
        self.allFeatures = list(self.featureCount.keys())
        self.featureCount = self.featureCount
        
    def getFeatures(self):
        return self.allFeatures
    
    def getFeatureCount(self):
        return self.featureCount
    
    def getHybrids(self, feature, subtype):
        IDs = []
        for ID in self.featureDict[subtype]:
            if feature in self.featureDict[subtype][ID]:
                IDs.append(ID)
        
        unbondedHybrids, bondedHybrids = getHybridsFromIDFile(self.IDDataPath + subtype + "data.json", verbose=False)
        allHybrids = unbondedHybrids + bondedHybrids
        hybrids = []
        for hybrid in allHybrids:
            if hybrid.testID in IDs:
                hybrids.append(hybrid)
        return hybrids

def main():
    subtypes = getECSubtypes()
    featureDict = {}

    for subtype in subtypes:
        filename = subtype + "FeatureDict.json"
        with open(filename, "r") as f:
            featureDict[subtype] = json.load(f)

    featureCount = {}
    for key in featureDict:
        for ID in featureDict[key]:
            theseFeatures = featureDict[key][ID]
            for feature in theseFeatures:
                if not feature in featureCount.keys():
                    featureCount[feature] = 0
                featureCount[feature] += 1

    print(featureCount)
    
if __name__ == "__main__":
    main()