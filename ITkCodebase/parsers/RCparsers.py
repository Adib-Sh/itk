"""
Parsers for Response Curve test results files, both .txt and .json formats.
Interface is parseRC(), which is file format agnostic.
"""

import json
import sys, os

from math import sqrt

sys.path.append(".." + os.sep)
from RCHelpers.RCHybrid import *

def parseRC(filename, readstream0=True, readstream1=True, verbose=True):
    
    extension = filename.split(".")[-1]
    parser = {"txt" : parseTxtRC, "json" : parseJsonRC}
    
    return parser[extension](filename, readstream0, readstream1, verbose=verbose)



def parseTxtRC(filepath, readstream0=True, readstream1=True, verbose=True):

    hybrid = RCHybrid()
    hybrid.fileFormat = "txt"
    
    chip = RCChip(-1) # Using dummy address since there is no address information in txt files
    
    with open(filepath) as csvfile:
        lines = csvfile.readlines()[1:]
        
    nChannels = len(lines)
    streamLength = nChannels // 2
    stream0 = []
    stream1 = []
    
    for n in range(streamLength):
        # Assuming chip 0 has channels [0:128] and [streamLength:streamLength+128]
    
        if n % 128 == 0 and n != 0:
            if readstream0:
                chip.channels.extend(stream0)
            if readstream1:
                chip.channels.extend(stream1)
            hybrid.addChip(chip)
            chip = RCChip(-1)
            stream0 = []
            stream1 = []
        
        s = lines[n].strip("\n").split("\t")
        stream0.append(RCChannel(int(s[0]), float(s[2]), float(s[3]), int(s[4]), 0, s[5]))
        s = lines[streamLength + n].strip("\n").split("\t")
        stream1.append(RCChannel(int(s[0]), float(s[2]), float(s[3]), int(s[4]), 1, s[5]))
        
    if readstream0:
        chip.channels.extend(stream0)
    if readstream1:
        chip.channels.extend(stream1)
    hybrid.addChip(chip)

    return hybrid
    
    
def parseJsonRC(filepath, readstream0=True, readstream1=True, verbose=True, peakMasking=False):

    channelsPerChip = 256
          
    if verbose:
        print("Parsing file:", filepath)
    if filepath[-4:] != "json":
        if verbose:
            print("Unknown format - needs to be a .json file! Skipping.")
        return None
    
    with open(filepath, 'rb') as jsonfile:
        data = json.load(jsonfile)
    
    try:
        testType = data["testType"]
        if isinstance(testType, dict):
      	    testType = testType['code']
    except KeyError:
        if verbose:
            print("Key \"testType\" not in file. Skipping:")
        return None
        
    if "RESPONSE_CURVE" not in testType:
        if verbose:
            print("Test type not recognized:", testType + ". Skipping.")
        return None
    
    try:
        testedAtStage = data["components"][0]["testedAtStage"]["code"]
    except:
        if verbose:
            print("Could not grab 'testedAtStage' information from json.")
        testedAtStage = None
    
    loadedResults = data['results']
    gain_under = None
    gain_away = None
    vt50_under = None
    vt50_away = None
    innse_under = None
    innse_away = None


    if isinstance(data['results'], list):
        for x in data['results']:
            if x['code'] == 'gain_under':
                gain_under = x['value']
            if x['code'] == 'gain_away':
                gain_away = x['value']    
            if x['code'] == 'vt50_under':
                vt50_under = x['value']
            if x['code'] == 'vt50_away':
                vt50_away = x['value']
            if x['code'] == 'innse_under':
                innse_under = x['value']
            if x['code'] == 'innse_away':
                innse_away = x['value']
                
    else:
        #other format
        gain_under = loadedResults['gain_under']
        gain_away = loadedResults['gain_away']
        vt50_under = loadedResults['vt50_under']
        vt50_away = loadedResults['vt50_away']
        innse_under = loadedResults['innse_under']
        innse_away = loadedResults['innse_away']
        #comment = [" "] * 2560
    
    # NB: Address numbering is not directly obvious, as it depends on module subtype. Some hybrids count from 0 and up, other count from 10 and down.
    addresses = None
    HCCTempRaw = None
    avgABCTemp = None
    ABCTemps = None
    if isinstance(data['properties'], list):
        for x in data['properties']:
            if x['code'] == 'det_info':
                addresses = x['value']['Address']
            if x['code'] == 'DCS':
                temperatureDict = x['value']
                HCCTempRaw = temperatureDict['HCC_temp_raw']
                numABCs = 0
                avgABCTemp = 0
                ABCTemps = {}
                for key in temperatureDict:
                    if "ABC" in key:
                        numABCs += 1
                        avgABCTemp += temperatureDict[key]
                        address = key.split("_")[-1]
                        ABCTemps[address] = temperatureDict[key]
                avgABCTemp /= numABCs
                    
    else:
        addresses = data['properties']['det_info']['Address']
        #HCCTempRaw = data['properties']['DCS']['HCC_temp_raw']
    n_chips = len(addresses)
    if verbose:
        print("Addresses", addresses)
    
    if "components" in data.keys():
        subtype = data['components'][0]['type']['code']
    else:
        subtype = None
        print("Could not grab subtype from json.")
    testID = filepath.split(os.sep)[-1].split(".")[0]
    
    hybrid = RCHybrid()
    hybrid.fileFormat = "json"
    hybrid.testedAtStage = testedAtStage
    hybrid.subtype = subtype
    hybrid.testID = testID
    hybrid.temperature = HCCTempRaw
    hybrid.HCCTempRaw = HCCTempRaw
    hybrid.avgABCTemp = avgABCTemp
    hybrid.ABCTemps = ABCTemps
    if "stateTs" in data.keys():
        hybrid.testDate = data["stateTs"]
    else:
        hybrid.testDate = data["date"]
        
    # Add ITSDAQ-generated comments to channels
    defects = {0 : {}, 1 : {}}
    if "defects" in data.keys():
        for defect in data["defects"]:
            comment = defect["name"]
            properties = defect["properties"]
            stream = {"under" : 0, "away" : 1}[properties["chip_bank"]]
            if "channel_from" in properties.keys():
                channels = list(range(properties["channel_from"], properties["channel_to"] + 1))
            elif "channel" in properties.keys():
                channels = [properties["channel"]]
            else:
                print("Warning - found ITSDAQ defect flag with no channel number:")
                print(defect)
                continue
            for channel in channels:
                defects[stream][channel] = "ITSDAQ:" + comment
    
    try:
        i = 0
        for address in addresses:
            if address is not None:
                
                if peakMasking and i == 5:
                    i += 1
                    continue
                
                chip = RCChip(address)
                stream0 = []
                stream1 = []
                for c in range(channelsPerChip // 2):
                    chanNum = c + i * channelsPerChip//2
                    stream0.append(RCChannel(chanNum, gain_under[i][c], vt50_under[i][c], innse_under[i][c], 0, comment=defects[0][chanNum] if chanNum in defects[0].keys() else ""))
                    stream1.append(RCChannel(chanNum, gain_away[i][c], vt50_away[i][c], innse_away[i][c], 1, comment=defects[1][chanNum] if chanNum in defects[1].keys() else ""))
                if readstream0:
                    chip.channels.extend(stream0)
                if readstream1:
                    chip.channels.extend(stream1)
                hybrid.addChip(chip, readstream0, readstream1)
                i += 1
    except:
        if verbose:
           print("Something went wrong in parsing! Returning empty hybrid.")
           print("Some hints to the problem: Lowest gain value",
                 min([channel.gain for channel in hybrid.channels]),
                 "Lowest innse value", min([channel.innse for channel in hybrid.channels]))
        hybrid.fileFormat = "error"
         
    cloned = checkClonedChipsBug(hybrid)
    if cloned:        
        tempHybrid = RCHybrid()
        tempHybrid.addChip(hybrid.chips[0], readstream0, readstream1)
        tempHybrid.fileFormat = "json (clone bug)"
        tempHybrid.testedAtStage = hybrid.testedAtStage
        tempHybrid.subtype = hybrid.subtype
        tempHybrid.testID = hybrid.testID
        tempHybrid.testDate = hybrid.testDate
        tempHybrid.HCCTempRaw = hybrid.HCCTempRaw
        tempHybrid.avgABCTemp = hybrid.avgABCTemp
        tempHybrid.ABCTemps = hybrid.ABCTemps
        if verbose:
            print("WARNING! Cloned chips detected! Returning hybrid with only one chip.")
        return tempHybrid
    
    return hybrid

def checkClonedChipsBug(hybrid):
    cloned = True
    for channelChip0, channelChip1 in zip(hybrid.chips[0].channels, hybrid.chips[1].channels):
        if channelChip0.innse != channelChip1.innse:
            cloned = False
    return cloned
