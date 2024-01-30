"""
Need to add a metadata key after the fact? No problem! Run the postfixer!

Note that this script is destructive, in the sense that it can overwrite
certain metadata keys without asking. Be sure to know what you're doing!
"""

import glob
import sys
import json
from metadataHelpers import getModuleTypes, getItkdbClient

def postfix(mode=None, inputFile=None):
    
    print("Mode:", mode, "\nInput file:", inputFile)

    dataPath = "../data/PRR/"

    moduleTypes = getModuleTypes()
    
    if mode == "getMetadataFiles":
        metadataFiles = []
        for moduleType in moduleTypes:
            path = dataPath + moduleType + "/"
            print(path)
            metadataFiles.extend(glob.glob(path + "**/metadata.json", recursive=True))
        return metadataFiles
       
    if mode == "moduleSNfix":
        # Uses a dictionary in a json built by buildModuleSNDict.py
        metadataFiles = postfix(mode="getMetadataFiles")
        with open(inputFile, "r") as f:
            moduleHybridDict = json.load(f)
        
        for metadataFile in metadataFiles:
            with open(metadataFile, "r") as f:
                storedMetadata = json.load(f)
            if storedMetadata["ModuleType"] in ["R3", "R4", "R5"]:
                for moduleSN in moduleHybridDict:
                    if storedMetadata["HybridSN"] in moduleHybridDict[moduleSN]:
                        if storedMetadata["ModuleSN"] == "Unknown":
                            storedMetadata["ModuleSN"] = moduleSN
                            print("Rewriting file", metadataFile)
                            print(storedMetadata)
                            print()
                            with open(metadataFile, "w") as f:
                                json.dump(storedMetadata, f, indent=2)
                            break
                        else:
                            print("Hybrid", storedMetadata["HybridSN"], "already has module SN:", storedMetadata["ModuleSN"])
                            break
    
    if mode == "halfModuleSNfix":
        # Grabs half module SN from database and adds it to each test metadata.json
        # Useful when one accidentally overwrites said half module SNs...
        metadataFiles = postfix(mode="getMetadataFiles")
        moduleType = inputFile # Uggly repurposing on input syntax
        if not moduleType:
            print("Please specify module type as input.")
            sys.exit(1)
        client = getItkdbClient()
        for metadataFile in metadataFiles:
            with open(metadataFile, "r") as f:
                storedMetadata = json.load(f)
            if storedMetadata["ModuleType"] == moduleType:
                hybridComponent = client.get("getComponent", json={"component" : storedMetadata["HybridSN"]})
                parents = hybridComponent["parents"]
                for parent in parents:
                    if parent["componentType"]["code"] == "MODULE":
                        halfModuleSN = parent["component"]["serialNumber"]
                        break
                storedMetadata["HalfModuleSN"] = halfModuleSN
                with open(metadataFile, "w") as f:
                    json.dump(storedMetadata, f, indent=2)
    
    if mode == "halfModuleTypeFix":
        # Grabs half module type from database and adds it to each test metadata.json
        metadataFiles = postfix(mode="getMetadataFiles")
        moduleType = inputFile # Uggly repurposing on input syntax
        if not moduleType:
            print("Please specify module type as input.")
            sys.exit(1)
        client = getItkdbClient()
        for metadataFile in metadataFiles:
            with open(metadataFile, "r") as f:
                storedMetadata = json.load(f)
            if storedMetadata["ModuleType"] == moduleType:
                hybridComponent = client.get("getComponent", json={"component" : storedMetadata["HybridSN"]})
                print(storedMetadata["HybridSN"]+ " - ", end="")
                parents = hybridComponent["parents"]
                for parent in parents:
                    if parent["componentType"]["code"] == "MODULE":
                        halfModuleComponent = client.get("getComponent", json={"component" : parent["component"]["serialNumber"]})
                        halfModuleType = halfModuleComponent["type"]["code"]
                        print(halfModuleType)
                        print()
                        break
                storedMetadata["HalfModuleType"] = halfModuleType
                with open(metadataFile, "w") as f:
                    json.dump(storedMetadata, f, indent=2)

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    postfix(*args)