import time

import itkdb
import json
import sys, os
sys.path.append("../")
sys.path.append(os.getcwd())
from loadPDBCredentials import loadCredentials
from resultCollector import collectResults
from RCHelpers.RCHybrid import RCHybrid
from parsers.RCparsers import parseRC, parseJsonRC

def isResponseCurve(js):
    if isinstance(js["properties"], dict):
        return len(js["properties"]["scan_info"]["points"]) == 10
    if isinstance(js["properties"], list):
        for item in js["properties"]:
            if item["code"] == "scan_info":
                return len(item["value"]["points"]) == 10
        
def getItkdbClient():
    cwd = os.getcwd()
    os.chdir("../")
    loadCredentials()
    os.chdir(cwd)
    user = itkdb.core.User(accessCode1=os.environ['ITKDB_ACCESS_CODE1'], accessCode2=os.environ['ITKDB_ACCESS_CODE2'])
    user.authenticate()
    client = itkdb.Client(user=user)
    return client

def processHybridSN(js, client):
    metadata = {}
    metadata["HybridSN"] = None
    if "component" in js.keys():
        metadata["HybridSN"] = js["component"]
    elif "components" in js.keys():
        metadata["HybridSN"] = js["components"][0]["serialNumber"]
    if not metadata["HybridSN"]:
        print("\033[91mFatal! Could not get HybridSN from file.\n\033[0m")
        return None
    
    hybridComponent = client.get("getComponent", json={"component" : metadata["HybridSN"]})
    parents = hybridComponent["parents"]
    metadata["ModuleSN"] = None
    for parent in parents:
        if not parent:
            print("Parent of hybrid", metadata["HybridSN"], "returned None.")
        elif parent["componentType"]["code"] == "MODULE":
            metadata["ModuleSN"] = parent["component"]["serialNumber"]
            break
    if not metadata["ModuleSN"]:
        print("WARNING - Could not get parent module from database.")
    
    metadata["HybridType"] = hybridComponent["type"]["code"][2:]
    
    metadata["ABCStarVersion"] = None
    metadata["HCCStarVersion"] = None
    for child in hybridComponent["children"]:
        if child["component"]:
            if child["componentType"]["code"] == "ABC":
                metadata["ABCStarVersion"] = child["type"]["code"]
            if child["componentType"]["code"] == "HCC":
                metadata["HCCStarVersion"] = child["type"]["code"]
        if metadata["ABCStarVersion"] and metadata["HCCStarVersion"]:
            break
    
    moduleComponent = client.get("getComponent", json={"component" : metadata["ModuleSN"]})
    
    # SO HERE: Figure out what kind of module it is.
    # R0 or R1? Just go.
    # R2? Do the H0 or H1 check like already implemented.
    # R3-R5? Make sure to put the SN in "HalfModule"
    # Then make sure that the results file sorter uses the correct key for folder structuring.
    
    # These if statements handle the slightly different metadata structures for different module types
    moduleTypeInfo = moduleComponent["type"]["code"]
    if moduleTypeInfo in ["R0", "R1"]:
        metadata["ModuleType"] = moduleTypeInfo[:2]
        metadata["HalfModuleType"] = "N/A"
        metadata["HalfModuleSN"] = "N/A"
    elif moduleTypeInfo == "R2":
        metadata["ModuleType"] = moduleTypeInfo[:2]
        metadata["HalfModuleType"] = "N/A"
        metadata["HalfModuleSN"] = "N/A"
        if isinstance(js["properties"], dict):
            if "H1" in js["properties"]["det_info"]["DUT_type"]:
                metadata["HybridType"] = "H1"
            elif "H1" in js["properties"]["det_info"]["name"]:
                metadata["HybridType"] = "H1"
            elif "H0" not in js["properties"]["det_info"]["DUT_type"] and "H0" not in js["properties"]["det_info"]["name"]:
                print("Fatal - Could not identify R2 hybrid type from json file.")
                print("This information can sometimes be found under 'det_info' : 'DUT_type' or 'name'.")
                sys.exit(1)
        elif isinstance(js["properties"], list):
            for item in js["properties"]:
                if item["code"] == "det_info":
                    if "H1" in item["value"]["DUT_type"]:
                        metadata["HybridType"] = "H1"
                    elif "H1" in item["value"]["name"]:
                        metadata["HybridType"] = "H1"
                    elif "H0" not in item["value"]["DUT_type"] and "H0" not in item["value"]["name"]:
                        print("Fatal - Could not identify R2 hybrid type from json file.")
                        print("This information can sometimes be found under 'det_info' : 'DUT_type' or 'name'.")
                        sys.exit(1)
    elif moduleTypeInfo[:2] in ["R3", "R4", "R5"]:
        metadata["HalfModuleType"] = moduleTypeInfo
        metadata["HalfModuleSN"] = metadata["ModuleSN"]
        metadata["ModuleType"] = moduleTypeInfo[:2]
        metadata["ModuleSN"] = "Unknown"
    else:
        print("\033[91mFatal! Unknown module type:", moduleTypeInfo, "\n\033[0m")
        return None
    
    metadata["Timestamp"] = js["date"]
    
    testRuns = hybridComponent["tests"]
    metadata["ModuleStage"] = "Unknown"
    for testRun in testRuns:
        if testRun["code"] == "RESPONSE_CURVE_PPA":
            testResults = None
            try:
                testResults = client.get("getTestRun", json={"testRun" : testRun["id"]})
            except Exception as ex:
                template = "Did not find test in database. Reason:\nAn exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print("\n" + message + "\n")
            
            if testResults:
                if isResponseCurve(testResults) and testResults["date"] == js["date"]:
                    metadata["ModuleStage"] = testResults["components"][0]["testedAtStage"]
        if metadata["ModuleStage"] != "Unknown":
            break
    
    return metadata

def getMetadataFromJson(js, client):
    metadata = processHybridSN(js, client)
    metadataKeys = getMetadataKeys()
    for key in metadataKeys:
        if key not in metadata.keys():
            metadata[key] = "Unknown"
    return metadata

def checkFolder(folderName):
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    
def getMetadataKeys(metadataType="test"):
    if metadataType == "test":
        return ["ModuleType",
                "HalfModuleType",
                "HybridType",
                "ModuleSN",
                "HalfModuleSN",
                "HybridSN",
                "Timestamp",
                "ABCStarVersion",
                "HCCStarVersion",
                "ModuleStage",
                "Temperature",
                "TemperatureCategory",
                "PartOfCycle",
                "CycleNumber",
                "CycleWarmTest",
                "Shunted",
                "DefaultConfig",
                "GroundingIssues",
                "Submitter",
                "Institute",
                "HandPicked"]
    if metadataType == "module":
        return ["PWBVersion",
                "GlueSpecies"]
    if metadataType == "all":
        metadataKeys = getMetadataKeys(metadataType="test")
        metadataKeys.extend(getMetadataKeys(metadataType="module"))
        return metadataKeys 
    print("Bad metadata type:", metadataType, "\n")
    return None

def getModuleTypes():
    # Returns a dict with module types and hybrid types;
    # {"R0" : ["H0", "H1"], "R1" : etc. ... }
    with open("metadataHandler/moduleTypes.json", "r") as f:
        moduleTypes = json.load(f)
    return moduleTypes

def getModuleHalfModuleTypes():
    # Returns a dict with module/half module types (where applicable) and hybrid types;
    # {"R0" : ["H0", "H1"], "R1" : etc. ... }
    with open("metadataHandler/moduleHalfModuleTypes.json", "r") as f:
        moduleTypes = json.load(f)
    return moduleTypes

def buildModuleMetadata(moduleType, moduleSN, client):
    dataPath = "../data/PRR/"
    metadataTemplate = {"PWBVersion" : "Unknown",
                        "GlueSpecies" : "Unknown"}
    path = dataPath
    if os.path.isdir(dataPath + moduleType):
        path += moduleType + "/"
        metadataFile = path + moduleSN + "/moduledata.json"
        if not os.path.exists(metadataFile):
            moduleComponent = client.get("getComponent",
                                         json={"component" : moduleSN})
            children = moduleComponent["children"]
            foundPWB = False
            PWBSN = None
            for child in children:
                if child["componentType"]["code"] == "PWB":
                    if foundPWB:
                        print("\33[33mWarning: multiple PWBs on module", moduleSN + ".\33[0m")
                    foundPWB = True
                    if child["component"]:
                        PWBSN = child["component"]["serialNumber"]
                        PWBComponent = client.get("getComponent", json={"component" : PWBSN})
                        properties = PWBComponent["properties"]
                        for property in properties:
                            if property["code"] == "VERSION":
                                PWBVersion = property["value"]
                                metadataTemplate["PWBVersion"] = PWBVersion
                                break
                        break
            if not PWBSN:
                print("Could not get PWBVersion for module", moduleSN + ".")

            print("Writing to metadata", metadataTemplate)
            print("to file", metadataFile, "\n")
            with open(metadataFile, "w") as f:
                json.dump(metadataTemplate, f)
        else:
            print("Module metadata already exists for module", moduleSN, "\n")
                
def getTestTuples(criteria):
    selectedCriteria = {}
    for key in criteria:
        if criteria[key] != "Any":
            selectedCriteria[key] = criteria[key]
    collectedResults = collectResults(selectedCriteria)
    collectedResults.sort(key=lambda result : result[0])
    return collectedResults

def getModulesForClassification(moduleType, criteria, returnHybrids=False):
       
    moduleTypesDict = getModuleHalfModuleTypes()
    if moduleType in ["R3", "R4", "R5"]:
        moduleTypes = [moduleType+subtype+"_HALFMODULE" for subtype in ["M0", "M1"]]
    else:
        moduleTypes = [moduleType]
        
    allModules = []
    allModuleSNsUsed = []
    hybridDict = {}
    for moduleType in moduleTypes:
        modules = []
        moduleSNsUsed = []
        testTuples = []
        print()
        print("Working on", moduleType)
        hybridTypes = moduleTypesDict[moduleType]
        for hybridType in hybridTypes:
            selectedCriteria = criteria.copy()
            selectedCriteria["HybridType"] = hybridType
            testTuples.extend(getTestTuples(selectedCriteria))
        
        moduleDict = {}
        for result, metadata in testTuples:
            # Group the types with half modules, i.e. R3, R4 and R5, per half module
            if moduleType[:2] in ["R3", "R4", "R5"]:
                moduleSN = metadata["HalfModuleSN"]
            else:
                moduleSN = metadata["ModuleSN"]
                
            if moduleSN not in moduleDict.keys():
                moduleDict[moduleSN] = {}
            
            hybridType = metadata["HybridType"]
            if hybridType in moduleDict[moduleSN]:
                print("\033[93mWarning! Multiple tests for hybrid of type", hybridType, "found for module", moduleSN + ". Using first one found.\033[0m\n")
            else:
                moduleDict[moduleSN][hybridType] = result
        
        nHybridsPerModule = len(hybridTypes)
        
        for moduleSN in moduleDict:
            
            print("\nWorking on module", moduleSN)
        
            if len(moduleDict[moduleSN]) < nHybridsPerModule:
                for hybridType in hybridTypes:
                    if hybridType not in moduleDict[moduleSN].keys():
                        print("\033[93mWarning! No test for hybrid of type", hybridType, "found for module", moduleSN + ". Skipping module.\033[0m\n")
            else:
                module = RCHybrid()
                module.subtype = moduleType
                for hybridType in moduleDict[moduleSN]:
                    
                    print("Working on hybrid type", hybridType)

                    result = moduleDict[moduleSN][hybridType]
                    
                    peakMasking = False
                    if moduleType[:2] in ["R4", "R5"]:
                        peakMasking = True
                        print("Masking module of type", moduleType[:2])
                    
                    hybrid = parseJsonRC(result, peakMasking=peakMasking)
                    hybrid.subtype = moduleType[:2] + hybridType
                    
                    # TODO: Should the returning hybrids be classified or not?
                    if returnHybrids:
                        if hybridType not in hybridDict.keys():
                            hybridDict[hybridType] = []
                        hybridDict[hybridType].append(hybrid)
                    
                    hybrid.classification(strategy="TypeSpecific")
                    
                    # Remove hybrid.badModule flag if it only has the >2% BAD CHAN flag, in order to:
                    # Make sure one hybrid with >2% bad channels doesn't kill the entire module, if it has more than one hybrid
                    removeComment = False
                    for comment in hybrid.fault:
                        if "2%" in comment:
                            removeComment = True
                    if removeComment:
                        hybrid.fault.remove(">2% BAD CHAN")
                    if hybrid.fault.isEmpty():
                        hybrid.badModule = False
                    
                    # Exclude module if the "IncludeBad" criteria is false
                    if "IncludeBad" in criteria.keys():
                        if criteria["IncludeBad"] == False and (module.badModule or hybrid.badModule):
                            module.badModule = True # To make sure a second good hybrid on the module doesn't include the module
                            break
                    
                    for chip in hybrid.chips:
                        module.addChip(chip)
                    
                    if hybrid.badModule:
                        module.badModule = True
                        for comment in hybrid.fault:
                            module.fault.append(comment)
                
                # Do 2% check for entire module
                includeModule = True
                numChannels = len(module.channels)
                if numChannels == 0:
                    print("Excluding module", moduleSN, "- no good hybrids available.")
                    includeModule = False
                else:
                    numBad = sum([channel.badchannel for channel in module.channels])
                    badFraction = numBad / numChannels
                    if badFraction > 0.02:
                        module.badModule = True
                        module.fault.append(">2% BAD CHAN")
                
                # Exclude bad module if the "IncludeBad" criteria is false
                if "IncludeBad" in criteria.keys():
                    if criteria["IncludeBad"] == False and (module.badModule):
                        print("Excluding bad module", moduleSN)
                        includeModule = False
                if includeModule:       
                    print("Appending hybrid of type", hybridType, "to module", moduleSN)
                    modules.append(module)
                    moduleSNsUsed.append(moduleSN)
                    print("All module SNs used so far:")
                    print(moduleSNsUsed)
                    
        allModules.append(modules)
        allModuleSNsUsed.append(moduleSNsUsed)
    if len(allModules) > 2:
        print("Fatal - something went wrong in gathering modules.")
        print("Could not pair up half modules.")
        sys.exit(1)
    
    if len(allModules) == 2:
        # Pair up half modules so that the left and right half come next to each other
        modules = []
        for halfModule1, halfModule2 in zip(allModules[0], allModules[1]):
            modules.append(halfModule1)
            modules.append(halfModule2)
        moduleSNsUsed = []
        for halfModuleSN1, halfModuleSN2 in zip(allModuleSNsUsed[0], allModuleSNsUsed[1]):
            moduleSNsUsed.append(halfModuleSN1)
            moduleSNsUsed.append(halfModuleSN2)
        # Check if excluding bad modules has left any unpaired half modules
        numRemaining = abs(len(allModules[0]) - len(allModules[1]))
        if numRemaining != 0:
            minNumber = min(len(allModules[0]), len(allModules[1]))
            if len(allModules[0]) > len(allModules[1]):
                for halfModule, halfModuleSN in zip(allModules[0][minNumber:], allModuleSNsUsed[0][minNumber:]):
                    modules.append(halfModule)
                    moduleSNsUsed.append(halfModuleSN)
            else:
                for halfModule, halfModuleSN in zip(allModules[1][minNumber:], allModuleSNsUsed[1][minNumber:]):
                    modules.append(halfModule)
                    moduleSNsUsed.append(halfModuleSN)
            
    if len(allModules) == 1:
        modules = allModules[0]
        moduleSNsUsed = allModuleSNsUsed[0]

    if returnHybrids:
        return modules, moduleSNsUsed, hybridDict
    else:
        return modules, moduleSNsUsed