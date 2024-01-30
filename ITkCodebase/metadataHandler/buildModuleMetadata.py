import os
import glob
from metadataHelpers import buildModuleMetadata, getItkdbClient, getModuleTypes

print("Building module metadata...")

client = getItkdbClient()

dataPath = "../data/PRR/"

moduleTypes = getModuleTypes()

for moduleType in moduleTypes:
    if os.path.isdir(dataPath + moduleType):
        moduleSNs = glob.glob(dataPath+moduleType+"/*")
        for item in moduleSNs:
            moduleSN = item.split("/")[-1]
            print("Processing", moduleType, moduleSN)
            buildModuleMetadata(moduleType, moduleSN, client)