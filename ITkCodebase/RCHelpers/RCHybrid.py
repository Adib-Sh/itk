from math import sqrt
import numpy as np
import json
import sys

CHIP_NOISE_SIGMA_LIMIT = 35.
CHIP_GAIN_SIGMA_LIMIT = 2.8

class RCChannel:
    def __init__(self, channelnumber: int, gain, vt50: float, innse: int, stream: int, comment=""):
        self.channelnumber = channelnumber
        self.gain = gain
        self.vt50 = vt50
        self.innse = innse
        self.stream = stream
        self.comment = CommentHandler(comment)
        # If the channel is initiated with an ITSDAQ-generated fault comment, mark it as bad
        if comment != "":
            self.badchannel = True
            self.ITSDAQbad = True
        else:
            self.badchannel = False
            self.ITSDAQbad = False

        self.outnse = 0.00016 * self.gain * self.innse

        self.unbonded = False
    
    def __str__(self):
        return "#chan: " + str(self.channelnumber) + " gain: " + str(self.gain) + " vt50: " + str(self.vt50) + " innse: " + str(self.innse) + " comment: " + str(self.comment)
    
    def classification(self, parentchip, strategy="ABC130", meanGain = None, sigmaGain = None, meanVt50 = None, sigmaVt50 = None, meanInnse = None, sigmaInnse = None, allowedSigma=None):
        """
        Strategies: "ABC130", "NathanR0RevisedGlobal", "NathanR0RevisedIteration"
        """
        
        if self.ITSDAQbad:
            return True, self.comment
        
        #low gain, high gain, low offset, high offset, unbonded, high noise
        comment = CommentHandler("OK")
        badchannel = False
        stream = self.stream
        
        #Basic strategy (As already found in ITSDAQ for the ABC130)
        if strategy == "ABC130":
            if self.gain < 0.75*parentchip.meanGain():
                badchannel = True
                comment.replace("OK", "LOW GAIN")
            if self.gain > 1.25*parentchip.meanGain():
                badchannel = True
                comment.replace("OK", "HIGH GAIN")
            if self.vt50 < parentchip.meanVt50()-80:
                badchannel = True
                comment.replace("OK", "LOW OFFSET")
            if self.vt50 > parentchip.meanVt50()+80:
                badchannel = True
                comment.replace("OK", "HIGH OFFSET")
            #Note cut on input noise and not output noise, which Nathan found to be suboptimal
            if self.innse < 540:
                badchannel = True
                self.unbonded = True
                comment.replace("OK", "UNBONDED")
            if self.innse > 1.15*parentchip.meanInnse():
                badchannel = True
                comment.replace("OK", "HIGH NOISE")

            self.badchannel = badchannel
            self.comment.replace("OK", comment)
                
            return badchannel, self.comment
       
        #Nathan's global R0 bad channel cut (NOTE: no unbonded) "STEP 1"
        if strategy == "NathanR0RevisedGlobal":
            if self.gain < 55:
                badchannel = True
                comment.replace("OK", "VERY LOW GAIN")
            if self.gain > 100:
                badchannel = True
                comment.replace("OK", "VERY HIGH GAIN")
            if self.innse < 300:
                badchannel = True
                comment.replace("OK", "VERY LOW NOISE")
            if self.innse > 1700:
                badchannel = True
                comment.replace("OK", "VERY HIGH NOISE")

            self.badchannel = badchannel
            self.comment.replace("OK", comment)
                
            return badchannel, self.comment

        if strategy == "TypeSpecificGlobal":
            if self.gain < 55:
                badchannel = True
                comment.replace("OK", "VERY LOW GAIN")
            if self.gain > 100:
                badchannel = True
                comment.replace("OK", "VERY HIGH GAIN")
            
            with open("QCstudy/noiseLimits.json", "r") as f:
                noiseLimitDict = json.load(f)
            subtype = parentchip.parentHybrid.subtype
            if subtype == "" or subtype is None:
                print("Channel does not have access to hybrid type. Classification fails.")
                sys.exit(1)
            highNoiseLimit = float(noiseLimitDict[subtype][str(self.stream)])
                
            if self.innse < 300:
                badchannel = True
                comment.replace("OK", "VERY LOW NOISE")
            if self.innse > highNoiseLimit:
                badchannel = True
                comment.replace("OK", "FAIL NOISE LIMIT")

            self.badchannel = badchannel
            self.comment.replace("OK", comment)
                
            return badchannel, self.comment

        # Global cuts, either type specific or Nathan's/Jacob's global cuts
        if strategy == "TypeSpecificIteration":
            globalbad, _ = self.classification(parentchip, strategy="TypeSpecificGlobal")
        if strategy == "NathanR0RevisedIteration":
            globalbad, _ = self.classification(parentchip, strategy="NathanR0RevisedGlobal")

        # Nathan's revised R0 strategy, one iteration of "STEP 2"
        if strategy == "TypeSpecificIteration" or strategy == "NathanR0RevisedIteration":
            
            if allowedSigma is None:
                allowedSigmas = parentchip.allowedSigmas
            elif isinstance(allowedSigma, int):
                allowedSigmas = {"gain" : allowedSigma, "innse" : allowedSigma, "outnse" : allowedSigma}
            if meanGain is None:
                meanGain = parentchip.meanGain(stream=stream, countbadchannels=False)
            if sigmaGain is None:
                sigmaGain = parentchip.sigmaGain(stream=stream, countbadchannels=False)
            if meanVt50 is None:
                meanVt50 = parentchip.meanVt50(stream=stream, countbadchannels=False)
            if sigmaVt50 is None:
                sigmaVt50 = parentchip.sigmaVt50(stream=stream, countbadchannels=False)
            if meanInnse is None:
                meanInnse = parentchip.meanInnse(stream=stream, countbadchannels=False)
            if sigmaInnse is None:
                sigmaInnse = parentchip.sigmaInnse(stream=stream, countbadchannels=False)
            
            if not (meanGain and sigmaGain and meanVt50 and sigmaVt50 and meanInnse and sigmaInnse):
                badchannel = True
                return badchannel, self.comment
            
            if strategy == "TypeSpecificIteration":
                subtype = parentchip.parentHybrid.subtype
                if subtype == "" or subtype is None:
                    print("Channel does not have access to hybrid type. Classification fails.")
                    sys.exit(1)
                with open("QCstudy/unbondedCuts.json", "r") as f:
                    unbondedCutsDict = json.load(f)
                unbondedCut = unbondedCutsDict[subtype][str(stream)]
            else:
                unbondedCut = 5.7 # 5.7 is the cut proposed for LS/SS by Jacob
            
            if self.outnse < unbondedCut: 
                self.unbonded = True
                badchannel = True
                comment.replace("OK", "UNBONDED")
            
            if globalbad:
                badchannel = True
                comment.replace("OK", "GLOBAL BAD")

            if not badchannel:

                if self.gain - meanGain < -allowedSigmas["gain"][stream]*sigmaGain:
                    badchannel = True
                    comment.replace("OK", "LOW GAIN")
                if self.gain - meanGain > allowedSigmas["gain"][stream]*sigmaGain:
                    badchannel = True
                    comment.replace("OK", "HIGH GAIN")
                if self.unbonded and self.innse - meanInnse < -allowedSigmas["innse"][stream]*sigmaInnse:
                    badchannel = True
                    comment.replace("OK", "LOW NOISE (UNBONDED)")
                if self.innse - meanInnse > allowedSigmas["innse"][stream]*sigmaInnse:
                    badchannel = True
                    comment.replace("OK", "HIGH NOISE")
                if self.vt50 - meanVt50 > 80:
                    badchannel = True
                    comment.replace("OK", "HIGH OFFSET")
                if self.vt50 - meanVt50 < -80:
                    badchannel = True
                    comment.replace("OK", "LOW OFFSET")
            
            self.badchannel = badchannel
            self.comment.replace("OK", comment)
                
            return badchannel, self.comment
   
    
class RCChip:
    def __init__(self, address: int, allowedSigmas=3.5): #ORIGINALLY allowedSigmas=3.5
        self.address = address
        self.channels = []
        self.comment = CommentHandler()
        self.badchip = False
        self.parentHybrid = None # This is set by RCHybrid.addChip
        if isinstance(allowedSigmas, float) or isinstance(allowedSigmas, int):
            self.allowedSigmas = {"gain" : [allowedSigmas]*2, "innse" : [allowedSigmas]*2, "outnse" : [allowedSigmas]*2}
        elif isinstance(allowedSigmas, dict):
            self.allowedSigmas = allowedSigmas
        else:
            print("Please provide allowedSigmas as either an int or dict = {\"gain\" : int, \"innse\" : int}")

    def meanGain(self, stream=None, countbadchannels=True):
        if stream is not None:
            channels = self.getStream(stream)
        else:
            channels = self.channels
        if countbadchannels:
            return sum([x.gain for x in channels])/len(channels)

        channels = [channel for channel in channels if channel.badchannel == False]
        if len(channels) == 0:
            return None
        return sum([x.gain for x in channels])/len([x for x in channels])
    
    def sigmaGain(self, stream=None, countbadchannels=True):
        meanGain = self.meanGain(stream=stream, countbadchannels=countbadchannels)
        if stream is not None:
            channels = self.getStream(stream)
        else:
            channels = self.channels
        if countbadchannels:
            return sqrt(sum([(x.gain-meanGain)**2 for x in channels])/len(channels))

        channels = [channel for channel in channels if channel.badchannel == False]
        if len(channels) == 0:
            return None
        return sqrt(sum([(x.gain-meanGain)**2 for x in channels])/len([x for x in channels]))

    def meanVt50(self, stream=None, countbadchannels=True):
        if stream is not None:
            channels = self.getStream(stream)
        else:
            channels = self.channels
        if countbadchannels:
            return sum([x.vt50 for x in channels])/len(channels)
        
        channels = [channel for channel in channels if channel.badchannel == False]
        if len(channels) == 0:
            return None
        return sum([x.vt50 for x in channels])/len([x for x in channels])
    
    def sigmaVt50(self, stream=None, countbadchannels=True):
        meanVt50 = self.meanVt50(stream=stream, countbadchannels=countbadchannels)
        if stream is not None:
            channels = self.getStream(stream)
        else:
            channels = self.channels
        if countbadchannels:
            return sqrt(sum([(x.vt50-meanVt50)**2 for x in channels])/len(channels))

        channels = [channel for channel in channels if channel.badchannel == False]
        if len(channels) == 0:
            return None
        return sqrt(sum([(x.vt50-meanVt50)**2 for x in channels])/len([x for x in channels]))
   
    def meanInnse(self, stream=None, countbadchannels=True):
        if stream is not None:
            channels = self.getStream(stream)
        else:
            channels = self.channels
        if countbadchannels:
            return sum([x.innse for x in channels])/len(channels)
        
        channels = [channel for channel in channels if channel.badchannel == False]
        if len(channels) == 0:
            return None
        return sum([x.innse for x in channels])/len([x for x in channels])
    
    def sigmaInnse(self, stream=None, countbadchannels=True):
        meanInnse = self.meanInnse(stream=stream, countbadchannels=countbadchannels)
        if stream is not None:
            channels = self.getStream(stream)
        else:
            channels = self.channels
        if countbadchannels:
            return sqrt(sum([(x.innse-meanInnse)**2 for x in channels])/len(channels))

        channels = [channel for channel in channels if channel.badchannel == False]
        if len(channels) == 0:
            return None
        return sqrt(sum([(x.innse-meanInnse)**2 for x in channels])/len([x for x in channels]))
    
    def meanOutnse(self, stream=None, countbadchannels=True):
        if stream is not None:
            channels = self.getStream(stream)
        else:
            channels = self.channels
        if countbadchannels:
            return sum([x.outnse for x in channels])/len(channels)
        
        channels = [channel for channel in channels if channel.badchannel == False]
        if len(channels) == 0:
            return None
        return sum([x.outnse for x in channels])/len([x for x in channels])
    
    def sigmaOutnse(self, stream=None, countbadchannels=True):
        meanOutnse = self.meanOutnse(stream=stream, countbadchannels=countbadchannels)
        if stream is not None:
            channels = self.getStream(stream)
        else:
            channels = self.channels
        if countbadchannels:
            return sqrt(sum([(x.outnse-meanOutnse)**2 for x in channels])/len(channels))

        channels = [channel for channel in channels if channel.badchannel == False]
        if len(channels) == 0:
            return None
        return sqrt(sum([(x.outnse-meanOutnse)**2 for x in channels])/len([x for x in channels]))

    def classification(self, streams=[0, 1], strategy = "ABC130"):

        #TODO All channels dead/stuck/inefficient
        #alldead = True
        #for channel in self.channels:

        badchip = False
        comment = CommentHandler()
        
        if not isinstance(streams, list):
            streams = [streams]

        #Basic ABC130 classification found in ITSDAQ
        if strategy == "ABC130":
            for stream in streams:
                if self.meanGain(stream=stream) < 0:
                    badchip = True
                    comment.append("LOW GAIN")
                if self.meanGain(stream=stream) > 140:
                    badchip = True
                    comment.append("HIGH GAIN")
                if self.meanVt50(stream=stream) < 0:
                    badchip = True
                    comment.append("LOW OFFSET")
                if self.meanVt50(stream=stream) > 120:
                    badchip = True
                    comment.append("HIGH OFFSET")
                if self.meanInnse(stream=stream) < 540:
                    badchip = True
                    comment.append("UNBONDED")
                if self.meanInnse(stream=stream) > 800:
                    badchip = True
                    comment.append("HIGH NOISE")
                    
                self.badchip = badchip or self.badchip
            self.comment.append(comment)
            return badchip, comment

        #Classification using Nathan's revised R0 scheme
        if strategy == "NathanR0Revised":
            
            for stream in streams:
                
                #Channel classification
                i = 0
                nBadIncrease = True
                nBad = 0
                nBadPrevious = 0
                
                allBad = True
                for channel in self.getStream(stream):
                    if not channel.badchannel:
                        allBad = False
                
                while i < 1000 and nBadIncrease and not allBad: # The while loop goes until an arbitrary cut-off designed to prevent stuck behaviour
                    i += 1
                    meanGain = self.meanGain(stream=stream, countbadchannels=False)
                    sigmaGain = self.sigmaGain(stream=stream, countbadchannels=False)
                    meanInnse = self.meanInnse(stream=stream, countbadchannels=False)
                    sigmaInnse = self.sigmaInnse(stream=stream, countbadchannels=False)
                    meanVt50 = self.meanVt50(stream=stream, countbadchannels=False)
                    sigmaVt50 = self.sigmaVt50(stream=stream, countbadchannels=False)
                    
                    allBad = True
                    
                    for channel in self.getStream(stream):

                        badchannel, _ = channel.classification(self, strategy="NathanR0RevisedIteration",
                                                     meanGain=meanGain, sigmaGain=sigmaGain,
                                                     meanInnse=meanInnse, sigmaInnse=sigmaInnse,
                                                     meanVt50=meanVt50, sigmaVt50=sigmaVt50)
                        nBad += badchannel
                        if not badchannel:
                            allBad = False
                                        
                    if not nBad > nBadPrevious:
                        nBadIncrease = False
                    else:
                        nBadPrevious = nBad
                        nBad = 0
                
                if allBad:
                    badchip = True
                    comment.append("STREAM " + str(stream) + " ALL BAD")
                    continue
                
                #Chip classification
                if self.sigmaGain(stream=stream, countbadchannels=False) > CHIP_GAIN_SIGMA_LIMIT:
                    badchip = True
                    comment.append("BAD CHIP GAIN SIGMA")
                if self.sigmaInnse(stream=stream, countbadchannels=False) > CHIP_NOISE_SIGMA_LIMIT:
                    badchip = True
                    comment.append("BAD CHIP NOISE SIGMA")
                    
                self.badchip = badchip or self.badchip
            self.comment.append(comment)
            return badchip, comment
            
        if strategy == "JacobChipSigma":
            for stream in streams:
       
                for var in ["gain", "innse"]:
                    iterations = 1
                    badSigma = True
                    sigmaStep = 0.1 # 0.1
                    sigmaLowerBound = 2 #2
                    sigmaFunc = {"gain": self.sigmaGain, "innse" : self.sigmaInnse}
                    sigmaLimits = {"gain" : CHIP_GAIN_SIGMA_LIMIT, "innse" : CHIP_NOISE_SIGMA_LIMIT}
                    
                    while badSigma and np.round(self.allowedSigmas[var][stream], decimals=1) >= sigmaLowerBound:
                        allBad = True
                        nBad = 0
                        for channel in self.getStream(stream):
                            if not channel.badchannel:
                                allBad = False
                            else:
                                nBad += 1
                        if allBad:
                            break
                                                
                        if sigmaFunc[var](stream=stream, countbadchannels=False) < sigmaLimits[var]:
                            badSigma = False
                        else:
                            self.allowedSigmas[var][stream] -= sigmaStep
                            # TODO: Refactor this to use self.classification(strategy="NathanR0Revised")
                            for i in range(10):
                                meanGain = self.meanGain(stream=stream, countbadchannels=False)
                                sigmaGain = self.sigmaGain(stream=stream, countbadchannels=False)
                                meanInnse = self.meanInnse(stream=stream, countbadchannels=False)
                                sigmaInnse = self.sigmaInnse(stream=stream, countbadchannels=False)
                                meanVt50 = self.meanVt50(stream=stream, countbadchannels=False)
                                sigmaVt50 = self.sigmaVt50(stream=stream, countbadchannels=False)
                                for channel in self.getStream(stream):
                                    channel.classification(self, strategy="NathanR0RevisedIteration",
                                                                 meanGain=meanGain, sigmaGain=sigmaGain,
                                                                 meanInnse=meanInnse, sigmaInnse=sigmaInnse,
                                                                 meanVt50=meanVt50, sigmaVt50=sigmaVt50)
                            self.comment.replace("STREAM" + str(stream) + " " + str(iterations-1) + " CHIP SIGMA CUT(S)",
                                                 "STREAM" + str(stream) + " " + str(iterations) + " CHIP SIGMA CUT(S)")
                        iterations += 1
                
            #Chip classification
            if allBad:
                badchip = True
                comment.append("STREAM " + str(stream) + " ALL BAD")
            else:
                if self.sigmaGain(stream=stream, countbadchannels=False) > CHIP_GAIN_SIGMA_LIMIT:
                    badchip = True
                    comment.append("BAD CHIP GAIN SIGMA")
                else:
                    self.comment.remove("BAD CHIP GAIN SIGMA")
                if self.sigmaInnse(stream=stream, countbadchannels=False) > CHIP_NOISE_SIGMA_LIMIT:
                    badchip = True
                    comment.append("BAD CHIP NOISE SIGMA")
                else:
                    self.comment.remove("BAD CHIP NOISE SIGMA")
                    
            self.badchip = badchip
            self.comment.append(comment)
            return badchip, comment
        
        # Using module and hybrid type-specific noise cuts
        if strategy == "TypeSpecific":
            
            for stream in streams:
                
                #Channel classification
                i = 0
                nBadIncrease = True
                nBad = 0
                nBadPrevious = 0
                
                allBad = True
                for channel in self.getStream(stream):
                    if not channel.badchannel:
                        allBad = False
                
                while i < 1000 and nBadIncrease and not allBad: # The while loop goes until an arbitrary cut-off designed to prevent stuck behaviour
                    i += 1
                    meanGain = self.meanGain(stream=stream, countbadchannels=False)
                    sigmaGain = self.sigmaGain(stream=stream, countbadchannels=False)
                    meanInnse = self.meanInnse(stream=stream, countbadchannels=False)
                    sigmaInnse = self.sigmaInnse(stream=stream, countbadchannels=False)
                    meanVt50 = self.meanVt50(stream=stream, countbadchannels=False)
                    sigmaVt50 = self.sigmaVt50(stream=stream, countbadchannels=False)
                    
                    allBad = True
                    
                    for channel in self.getStream(stream):

                        badchannel, _ = channel.classification(self, strategy="TypeSpecificIteration",
                                                                meanGain=meanGain, sigmaGain=sigmaGain,
                                                                meanInnse=meanInnse, sigmaInnse=sigmaInnse,
                                                                meanVt50=meanVt50, sigmaVt50=sigmaVt50)
                        nBad += badchannel
                        if not badchannel:
                            allBad = False
                                        
                    if not nBad > nBadPrevious:
                        nBadIncrease = False
                    else:
                        nBadPrevious = nBad
                        nBad = 0
                
                if allBad:
                    badchip = True
                    comment.append("STREAM " + str(stream) + " ALL BAD")
                    continue
                
                #Chip classification
                if self.sigmaGain(stream=stream, countbadchannels=False) > CHIP_GAIN_SIGMA_LIMIT:
                    badchip = True
                    comment.append("BAD CHIP GAIN SIGMA")
                if self.sigmaInnse(stream=stream, countbadchannels=False) > CHIP_NOISE_SIGMA_LIMIT:
                    badchip = True
                    comment.append("BAD CHIP NOISE SIGMA")
                    
                self.badchip = badchip or self.badchip
            self.comment.append(comment)
            return badchip, comment
        
        if strategy == "TypeSpecificChipSigma":
            allBad = {}
            for stream in streams:
       
                for var in ["gain", "innse"]:
                    iterations = 1
                    badSigma = True
                    sigmaStep = 0.1 # 0.1
                    sigmaLowerBound = 2 #2
                    sigmaFunc = {"gain": self.sigmaGain, "innse" : self.sigmaInnse}
                    sigmaLimits = {"gain" : CHIP_GAIN_SIGMA_LIMIT, "innse" : CHIP_NOISE_SIGMA_LIMIT}
                    
                    while badSigma and np.round(self.allowedSigmas[var][stream], decimals=1) >= sigmaLowerBound:
                        allBad[stream] = True
                        nBad = 0
                        for channel in self.getStream(stream):
                            if not channel.badchannel:
                                allBad[stream] = False
                            else:
                                nBad += 1
                        if allBad[stream]:
                            break

                        if sigmaFunc[var](stream=stream, countbadchannels=False) < sigmaLimits[var]:
                            badSigma = False
                        else:
                            self.allowedSigmas[var][stream] -= sigmaStep
                            # TODO: Refactor this to use self.classification(strategy="NathanR0Revised")
                            for i in range(10):
                                meanGain = self.meanGain(stream=stream, countbadchannels=False)
                                sigmaGain = self.sigmaGain(stream=stream, countbadchannels=False)
                                meanInnse = self.meanInnse(stream=stream, countbadchannels=False)
                                sigmaInnse = self.sigmaInnse(stream=stream, countbadchannels=False)
                                meanVt50 = self.meanVt50(stream=stream, countbadchannels=False)
                                sigmaVt50 = self.sigmaVt50(stream=stream, countbadchannels=False)
                                for channel in self.getStream(stream):
                                    channel.classification(self, strategy="TypeSpecificIteration",
                                                            meanGain=meanGain, sigmaGain=sigmaGain,
                                                            meanInnse=meanInnse, sigmaInnse=sigmaInnse,
                                                            meanVt50=meanVt50, sigmaVt50=sigmaVt50)
                            self.comment.replace("STREAM" + str(stream) + " " + str(iterations-1) + " CHIP SIGMA CUT(S)",
                                                 "STREAM" + str(stream) + " " + str(iterations) + " CHIP SIGMA CUT(S)")
                        iterations += 1
                
            #Chip classification
            for stream in streams:
                if allBad[stream]:
                    badchip = True
                    comment.append("STREAM " + str(stream) + " ALL BAD")
                else:
                    if self.sigmaGain(stream=stream, countbadchannels=False) > CHIP_GAIN_SIGMA_LIMIT:
                        badchip = True
                        comment.append("BAD CHIP GAIN SIGMA")
                    else:
                        self.comment.remove("BAD CHIP GAIN SIGMA")
                    if self.sigmaInnse(stream=stream, countbadchannels=False) > CHIP_NOISE_SIGMA_LIMIT:
                        badchip = True
                        comment.append("BAD CHIP NOISE SIGMA")
                    else:
                        self.comment.remove("BAD CHIP NOISE SIGMA")
                    
            self.badchip = badchip
            self.comment.append(comment)
            return badchip, comment
 
    def getStream(self, stream: int):
        
        if stream not in [0, 1]:
            print("Bad stream number. Please provide 0 or 1.")
            return None
        
        return self.channels[stream*len(self.channels)//2 : (stream+1)*len(self.channels)//2]

class RCHybrid:
    def __init__(self):
        self.chips = []
        self.channels = []
        self.stream0 = []
        self.stream1 = []
        self.fileFormat = ""
        self.testedAtStage = ""
        self.subtype = ""
        self.testID = ""
        self.testDate = ""
        self.temperature = None
        self.serialNumber = None

        self.badModule = None
        self.fault = CommentHandler()
    
    def __str__(self):
        return "#chips: " + str(len(self.chips)) + ", fileFormat: " + self.fileFormat + ", testedAtStage: " + self.testedAtStage + ", subtype: " + self.subtype
    
    def addChip(self, chip: RCChip, readstream0 = True, readstream1 = True):
        chip.parentHybrid = self
        self.chips.append(chip)
        self.channels.extend(chip.channels)
        if readstream0:
            self.stream0.extend(chip.channels[:128])
        if readstream1:
            if readstream0:
                self.stream1.extend(chip.channels[128:])
            else:
                self.stream1.extend(chip.channels[:128])
    
    def getStream(self, stream: int):
        if stream == 0:
            return self.stream0
        if stream == 1:
            return self.stream1
        print("WARNING: Please request stream 0 or 1.")
        return []
    
    def classification(self, strategy="Full"):
        for chip in self.chips:
            if strategy == "ABC130":
                chip.classification(strategy="ABC130")
            if strategy == "Full" or strategy == "NathanR0Revised":
                chip.classification(strategy="NathanR0Revised")
            if strategy == "Full" or strategy == "JacobChipSigma":
                chip.classification(strategy="JacobChipSigma")
            if strategy == "TypeSpecific":
                badchip, comment = chip.classification(strategy="TypeSpecific")
                badchip, comment = chip.classification(strategy="TypeSpecificChipSigma")
            if strategy == "TypeSpecificNoSigmaReduction":
                badchip, comment = chip.classification(strategy="TypeSpecific")

        self.badModule = False
        #Bad module classification
        for chip in self.chips:
            if chip.badchip == True:
                self.badModule = True
                self.fault.replace("", "BAD CHIP")
                break

        #Is this a fine way to iterate through channels, across the chip boundaries?

        totalBad = 0
        
        hybridUnder = self.getStream(0)
        hybridAway = self.getStream(1)
        
        badChannelStreakUnder = 0
        foundBadChannelStreakUnder = False

        for channel in hybridUnder:
            if channel.badchannel == True:
                badChannelStreakUnder += 1
                totalBad += 1
            elif channel.badchannel == False:
                badChannelStreakUnder = 0
            if badChannelStreakUnder > 8:
                foundBadChannelStreakUnder = True
        
        badChannelStreakAway = 0
        foundBadChannelStreakAway = False

        for channel in hybridAway:
            if channel.badchannel == True:
                totalBad += 1
                badChannelStreakAway += 1
            elif channel.badchannel == False:
                badChannelStreakAway = 0
            if badChannelStreakAway > 8:
                foundBadChannelStreakAway = True
   
        badFraction = totalBad / (len(hybridUnder)+len(hybridAway))
        
        if foundBadChannelStreakUnder or foundBadChannelStreakAway:
            self.badModule = True
            self.fault.replace("", "BAD CHAN STREAK")
        
        if badFraction > 0.02:
            self.badModule = True
            self.fault.replace("", ">2% BAD CHAN")

    def detectAnomalies(self, variable, windowSize = 16, streams = [0, 1], countbadchannels = False):
        
        if not isinstance(streams, list):
            streams = [streams]
        anomalyDict = {}
        skipStart = windowSize // 2
        skipEnd = windowSize - skipStart
        for stream in streams:
            anomalyDict[stream] = {}
            for chipNum, chip in enumerate(self.chips):
                anomalyDict[stream][chipNum] = []
                channels = chip.getStream(stream)
                if countbadchannels:
                    values = [{"innse" : channel.innse,
                               "outnse": channel.outnse,
                               "gain"  : channel.gain}[variable] for channel in channels]
                else:
                    values = [{"innse" : channel.innse,
                               "outnse": channel.outnse,
                               "gain"  : channel.gain}[variable] for channel in channels if not channel.badchannel]
                
                if len(values) == 0:
                    anomalyDict[stream][chipNum].append(str(stream)+"ALLBAD")
                    continue
                
                means = []
                sigmas = []
                for c in range(len(values) - windowSize):
                    means.append(np.mean(values[c:c+windowSize]))
                    sigmas.append(np.std(values[c:c+windowSize]))
                sigmaSigma = np.std(sigmas)
                meanMean = np.mean(means)
                sideMeans = (sum([mean-meanMean for mean in means[:len(means)//2]])/meanMean,
                             sum([mean-meanMean for mean in means[len(means)//2:]])/meanMean)
                                
                largeSigma = {"innse" : chip.sigmaInnse,
                              "outnse": chip.sigmaOutnse,
                              "gain"  : chip.sigmaGain}[variable](stream=stream, countbadchannels=False) > 35
                largeSigmaSigma = sigmaSigma > 2.5
                largeEndDiff = np.abs(sideMeans[0]) > 0.5
                if largeSigma and not largeEndDiff:
                    anomalyDict[stream][chipNum].append("FATCHIP")
                if largeSigmaSigma:
                    anomalyDict[stream][chipNum].append("FEATURED")
                if largeEndDiff:
                    anomalyDict[stream][chipNum].append("SLOPED")
        
        return anomalyDict

class CommentHandler:
    def __init__(self, comment = None):
        if isinstance(comment, str):
            if comment == "":
                self.commentList = []
                self.max = 0
            else:
                self.commentList = [comment]
                self.max = 1
        elif isinstance(comment, list):
            self.commentList = comment
            self.max = len(comment)
        elif isinstance(comment, CommentHandler):
            self.commentList = comment.commentList
            self.max = len(comment.commentList)
        elif comment is None:
            self.commentList = []
            self.max = 0
        else:
            raise TypeError("Bad comment construction. Unsupported type", type(comment))
    
    def isEmpty(self):
        return self.commentList == []
    
    def appendSingle(self, comment):
        if comment == "OK" and not self.isEmpty():
            return
        if comment not in self.commentList:
            self.commentList.append(comment)
            self.max += 1
        self.commentList.sort()
    
    def append(self, comment):
        if isinstance(comment, list):
            for c in comment:
                self.appendSingle(c)
        elif isinstance(comment, CommentHandler):
            for c in comment:
                self.appendSingle(c)
        elif isinstance(comment, str):
            self.appendSingle(comment)
        else:
            raise TypeError("Bad type. Cannot append type", type(comment))

    def remove(self, removeComment):
        if self.max > 0:
            for c, comment in enumerate(self.commentList):
                if comment == removeComment:
                    self.commentList.pop(c)
                    self.max -= 1
    
    def replace(self, toReplace, newComment):
        self.remove(toReplace)
        self.append(newComment)
            
    def __eq__(self, other):
        if isinstance(other, str):
            if len(self.commentList) > 1:
                return False
            if self.commentList == []:
                if other == "":
                    return True
                else:
                    return False
            if self.commentList[0] == other:
                return True
            return False
        elif isinstance(other, CommentHandler):
            for thisElement, otherElement in zip(self.commentList, other.commentList):
                if thisElement != otherElement:
                    return False
            return True
        elif isinstance(other, list):
            if len(self.commentList) != len(other):
                return False
            for thisElement, otherElement in zip(self.commentList, other):
                if thisElement != otherElement:
                    return False
            return True
        else:
            raise TypeError("Bad type comparison. Cannot compare CommentHandler to", type(other))
    
    def __iter__(self):
        self.c = 0
        return self
    
    def __next__(self):
        if self.c < self.max:
            currentComment = self.commentList[self.c]
            self.c += 1
            return currentComment
        else:
            raise StopIteration
    
    def __str__(self):
        string = ""
        if len(self.commentList) == 1:
            string = self.commentList[0]
        elif len(self.commentList) > 1:
            for comment in self.commentList[:-1]:
                string += comment + ", "
            string += self.commentList[-1]
        return string
    
    def __len__(self):
        return self.max
