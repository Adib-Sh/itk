import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.lines import Line2D
import numpy as np
import sys
import os
import json

from RCHelpers.RCHybrid import *
from analysis.Helpers.getHybridsFromIDFile import getHybridsFromIDFile
from analysis.Helpers.getCuts import getCuts
from scipy.optimize import curve_fit

def plotRCInnseTxt(results):
#
# NB: This is temporary, only to be used while figuring out the txt file structure.
#
    
    channelnumbers = []
    innses = []

    for chan in results.channels:
        channelnumbers.append(chan.channelnumber)
        innses.append(chan.innse)

    fig, (ax1, ax2) = plt.subplots(1,2, sharey=True, gridspec_kw={'width_ratios': [1,4]})

    bins = np.linspace(0, max(innses)+5,100)

    ax1.hist(innses, bins=bins, orientation="horizontal", color="black")
    ax1.invert_xaxis()
    ax1.set_ylabel("Innse [ENC]")
    ax1.set_xlabel("# of channels")
    
    ax2.set_xlim(0,max(channelnumbers))
    ax2.set_ylim(0,bins[-1])
    ax2.axvline(1280, *ax2.get_ylim(), alpha=0.2, linestyle='--')
    ax2.scatter(channelnumbers, innses, s=1, color="black", marker="s", alpha=1)
    ax2.set_xlabel("Channel #")
    
    plt.show()
    
    return ax2

def plotRCHistograms(hybrids, bondedList=None, variable="innse", streams=[0, 1],
                     yscale="linear", bins=None, fig=None, ax=None, metadata=None,
                     title=None, showNow=True, noiseLimit=None, gainLimits=None,
                     unbondedCuts=None, dataLabel="", color=None, hatch=None,
                     histtype=None):
    values = {}
    if not isinstance(hybrids, list):
        hybrids = [hybrids]
    if not isinstance(hybrids, np.ndarray):
        hybrids = np.array(hybrids)
        
    for stream in streams:
        values[stream] = []
    if bondedList:
        if len(hybrids) != len(bondedList):
            print("Lists of hybrids and bonded status do not match. Aborting.")
            sys.exit(1)
        values["unbonded"] = []
    else:
        bondedList = [True for _ in hybrids]
        
    if variable not in ["innse", "outnse", "gain", "vt50"]:
        print("Unknown variable:", variable + ". Aborting.")
        sys.exit(1)
    
    if not fig and not ax:
        fig, ax = plt.subplots()
      
    for hybrid, bondedStatus in zip(hybrids, bondedList):
        for stream in streams:
            theseValues = [{"gain"  : channel.gain,
                            "innse" : channel.innse,
                            "outnse": channel.outnse,
                            "vt50"  : channel.vt50}[variable] for channel in hybrid.getStream(stream)]
            values[{False : "unbonded", True : stream}[bondedStatus]].extend(theseValues)
    
    if not bins:
        nBins = 200
        binLimits = {"gain"  : [0, 150],
                     "innse" : [300, 1300],
                     "outnse": [0, 25],
                     "vt50"  : [0, 200]}[variable]
        bins = np.linspace(binLimits[0], binLimits[1], nBins)
    
    usedColorsDict = {}
    for key in values:
        nEntries = {True : len(hybrids) - sum(bondedList),
                    False : sum(bondedList)}[key == "unbonded"]
        separator = ", " if dataLabel != "" else ""
        label = dataLabel + separator  + {"unbonded" : f"Unbonded hybrids (N = {nEntries})",
                 0 : f"Under\n(N = {nEntries})",
                 1 : f"Away\n(N = {nEntries})"}[key]
        if not hatch:
            hatch = {"unbonded" : "x",
                    0 : "//",
                    1 : "\\\\"}[key]
        if not histtype:
            histtype = "step"
        if color:
            _, _, patches = ax.hist(values[key], bins=bins, histtype=histtype, linewidth=2,
                                label=label, hatch=hatch, color=color)
        else:
            _, _, patches = ax.hist(values[key], bins=bins, histtype=histtype, linewidth=2,
                                label=label, hatch=hatch)
        usedColorsDict[key] = patches[0].get_edgecolor()
    plt.subplots_adjust(left=0.1, right=0.99)
    
    if metadata:
        print("Including metadata in plot.")
        metadataStr = "Selected criteria\n"
        for key in metadata.keys():
            metadataStr += key + ": " + metadata[key] + "\n"
        plt.text(.65, .87, metadataStr, transform=fig.transFigure,
                 verticalalignment="top")
        plt.subplots_adjust(right=0.63)
    
    ax.set_yscale(yscale)
    xlabel = {"innse" : "Input noise [ENC]",
              "outnse": "Output noise [mV]",
              "gain"  : "Gain [mV/fC]",
              "vt50"  : "Vt50"}[variable]
    ylabel = "# channels"
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        plt.suptitle(title, fontsize=10)
    if noiseLimit and variable == "innse":
        ylims = ax.get_ylim()
        for stream in streams:
            color = usedColorsDict[stream]
            print("Color for stream", stream, "is:", color)
            print(noiseLimit[str(stream)])
            plt.axvline(x=float(noiseLimit[str(stream)]), ymin=ylims[0],
                        ymax=ylims[1],linestyle="--", color=color, label="High noise\nlimit, "+{0 : "under", 1 : "away"}[stream])
    if gainLimits and variable == "gain":
        ylims = ax.get_ylim()
        plt.axvline(x=gainLimits[0], ymin=ylims[0], ymax=ylims[1], linestyle="--",
                    color="grey", label="Absolute gain limits")
        plt.axvline(x=gainLimits[1], ymin=ylims[0], ymax=ylims[1], linestyle="--",
                    color="grey")
    if unbondedCuts and variable == "outnse":
        ylims = ax.get_ylim()
        for stream in streams:
            color = usedColorsDict[stream]
            linestyle = ":"
            unbondedCut = unbondedCuts[str(stream)]
            plt.axvline(x=unbondedCut, ymin=ylims[0], ymax=ylims[1], linestyle=linestyle,
                        color=color, label="Unbonded cut "+ {0 : "(under)", 1: "(away)"}[stream])
    ax.legend()
    if showNow:
        plt.show()
    return fig, ax

def plotRCCycleMeans(hybrids, variable="innse", streams=[0, 1], fig=None, ax=None, metadata=None, title=None, xlabels=None, showNow=True):
    # Currently assumes that hybrids are sorted by timestamp
    if not fig or not ax:
        fig, ax = plt.subplots()
    
    means = {}
    for stream in streams:
        means[stream] = []
        for hybrid in hybrids:
            channels = hybrid.getStream(stream)
            values = [{"gain"  : channel.gain,
                       "innse" : channel.innse,
                       "outnse": channel.outnse}[variable] for channel in channels]
            mean = np.mean(values)
            means[stream].append(mean)
        ax.plot(means[stream], 'o', label={0: "under",
                                   1: "away"}[stream])
    if xlabels:
        ax.set_xticks(list(range(len(hybrids))))
        ax.set_xticklabels(xlabels, rotation=90)
        plt.subplots_adjust(bottom=0.4)
    ax.set_ylabel({"gain"  : "Gain [mV/fC]",
                   "innse" : "Input noise [ENC]",
                   "outnse": "Output noise [mV]"}[variable])
    ax.legend()
    ax.grid()
    if title:
        plt.suptitle(title)
    if showNow:
        plt.show()
        
def plotResponseCurveGain(results):
    
    channelnumbers = []
    gains = []

    for chan in results.channels:
        channelnumbers.append(chan.channelnumber)
        gains.append(chan.gain)

    fig, (ax1, ax2) = plt.subplots(1,2, sharey=True, gridspec_kw={'width_ratios': [1,4]})

    bins = np.linspace(0, max(gains)+5,100)

    ax1.hist(gains, bins=bins, orientation="horizontal", color="black")
    ax1.invert_xaxis()
    ax1.set_ylabel("Gain [mV/ENC]")
    ax1.set_xlabel("# of channels")

    ax2.scatter(channelnumbers, gains, s=1, color="black", marker="s", alpha=0.2)
    ax2.set_xlim(0,max(channelnumbers))
    ax2.set_ylim(0,bins[-1])
    ax2.set_xlabel("Channel #")

    plt.show()

def plotRCGainHistograms(hybrids, yscale="linear", bins=None):
    """
    Plot a histogram of channels binned by gain. 
    hybrids is a list of hybrid class objects, yscale is the requested scale of the y-axis and bins is the
    requested bins (set to [min(gain)-5, max(gain)+5] with bin size 1 mV/fC if left blank).
    """
    
    # ====== NB ======
    # If working with bugged data, i.e., data from before the ITSDAQ JSON output patch, only use the first chip in each hybrid
    # Else, use all chips
    # ================
    
    gains = []
    
    if type(hybrids) != list:
        hybrids = [hybrids]
    
    for hybrid in hybrids:
        
        # EITHER, all chips
        #hybridGains = [hybrid.channels[c].gain for c in range(len(hybrid.channels))]
        
        # OR, only the first chip
        hybridGains = [hybrid.chips[0].channels[c].gain for c in range(len(hybrid.chips[0].channels))]
        
        gains.extend(hybridGains)
    
    if bins is None:
        gainMin = int(min(gains))
        gainMax = int(max(gains))
        n_bins = gainMax + 5 - (gainMin - 5)
        bins = np.linspace(min(gains)-5, max(gains)+5, n_bins)
    
    fig = plt.figure()
    
    plt.hist(gains, bins=bins)
    plt.yscale(yscale)
    plt.xlabel("Gain [mV/fC]")
    plt.ylabel("# channels")
    
    plt.show()

def plotRCInnseHistograms(hybrids, yscale="linear", bins=None, streams=[0, 1]):
    """
    Plot a histogram of channels binned by input noise (innse). 
    hybrids is a list of hybrid class objects, yscale is the requested scale of the y-axis and bins is the
    requested bins (set to [min(gain)-5, max(gain)+5] with bin size 1 mV/fC if left blank).
    """
    
    # ====== NB ======
    # If working with bugged data, i.e., data from before the ITSDAQ JSON output patch, only use the first chip in each hybrid
    # Else, use all chips
    # ================
    
    if type(hybrids) != list:
        hybrids = [hybrids]
    
    for stream in streams:
        innses = []
        fig, ax = plt.subplots()
        hc = 0
        for hybrid in hybrids:
            hc += 1
            # Use all chips
            if hybrid.fileFormat == "json":
                hybridInnse = [channel.innse for channel in hybrid.getStream(stream)]
                    
            # Or only the first one, in the case of a bugged json
            elif hybrid.fileFormat == "json (clone bug)":
                print(" ======= \n WARNING \n ======= \nDetected bugged json data!")
                hybridInnse = [hybrid.chips[0].channels[c].innse for c in range(len(hybrid.chips[0].channels))]
            
            else:
                hybridInnse = [channel.innse for channel in hybrid.getStream(stream)]
            
            innses.extend(hybridInnse)
        
        resetBins = False
        if bins is None:
            innseMin = 0 # int(min(innses))
            innseMax = min(int(max(innses)), 2000)
            n_bins = min(innseMax + 5 - (innseMin - 5), 200)
            bins = np.linspace(innseMin-5, innseMax+5, n_bins)
            resetBins = True

        print(innseMax)
        plt.hist(innses, bins)
        if resetBins:
            bins = None
        plt.yscale(yscale)
        plt.xlabel("Input noise [Electronic Noise Count(?) ENC]")
        plt.ylabel("# channels")
        plt.title("Input noise stream " + str(stream))
    
    plt.show()
    
    return fig, ax

def plotRCVt50Histograms(hybrids, yscale="linear", bins=None):
    """
    Plot a histogram of channels binned by input noise (innse). 
    hybrids is a list of hybrid class objects, yscale is the requested scale of the y-axis and bins is the
    requested bins (set to [min(gain)-5, max(gain)+5] with bin size 1 mV/fC if left blank).
    """
    
    # ====== NB ======
    # If working with bugged data, i.e., data from before the ITSDAQ JSON output patch, only use the first chip in each hybrid
    # Else, use all chips
    # ================
    
    vt50s = []
    
    if type(hybrids) != list:
        hybrids = [hybrids]
    
    for hybrid in hybrids:
        
        # EITHER, all chips
        #hybridvt50s = [hybrid.channels[c].vt50 for c in range(len(hybrid.channels))]
        
        # OR, only the first chip
        hybridvt50 = [hybrid.chips[0].channels[c].vt50 for c in range(len(hybrid.chips[0].channels))]
        
        vt50s.extend(hybridvt50)
    
    if bins is None:
        vt50Min = int(min(vt50s))
        vt50Max = int(max(vt50s))
        n_bins = vt50Max + 5 - (vt50Min - 5)
        bins = np.linspace(min(vt50s)-5, max(vt50s)+5, n_bins)
    
    fig = plt.figure()
    
    plt.hist(vt50s, bins)
    plt.yscale(yscale)
    plt.xlabel("Vt50 [mV/fC]]")
    plt.ylabel("# channels")
    
    plt.show()

def plotRCOutnseHistograms(hybrids, yscale="linear", bins=None):
    """
    Plot a histogram of channels binned by input noise (innse). 
    hybrids is a list of hybrid class objects, yscale is the requested scale of the y-axis and bins is the
    requested bins (set to [min(gain)-5, max(gain)+5] with bin size 1 mV/fC if left blank).
    """
    
    # ====== NB ======
    # If working with bugged data, i.e., data from before the ITSDAQ JSON output patch, only use the first chip in each hybrid
    # Else, use all chips
    # ================
    
    outnses = []
    
    if type(hybrids) != list:
        hybrids = [hybrids]
    
    for hybrid in hybrids:
        
        # EITHER, all chips
        #hybridoutnses = [hybrid.channels[c].outnse for c in range(len(hybrid.channels))]
        
        # OR, only the first chip
        hybridoutnse = [hybrid.chips[0].channels[c].outnse for c in range(len(hybrid.chips[0].channels))]
        
        outnses.extend(hybridoutnse)
    
    if bins is None:
        outnseMin = int(min(outnses))
        outnseMax = int(max(outnses))
        n_bins = outnseMax + 5 - (outnseMin - 5)
        bins = np.linspace(min(outnses)-5, max(outnses)+5, n_bins)
    
    fig = plt.figure()
    
    plt.hist(outnses, bins)
    plt.yscale(yscale)
    plt.xlabel("Outnse [mV/ENC]]]")
    plt.ylabel("# channels")
    
    plt.show()

def plotRCUnbondedClassificationOutnseHistograms(unbonded, bonded, yscale="linear", bins=None, title="None"):
    # ====== NB ======
    # If working with bugged data, i.e., data from before the ITSDAQ JSON output patch, only use the first chip in each hybrid
    # Else, use all chips
    # ================
    
    fig = plt.figure()
    
    for hybrids in [[unbonded,"Unbonded","all"], [bonded,"Bonded","stream0"], [bonded,"Bonded","stream1"]]:
        outnses = []

        if type(hybrids[0]) != list:
            hybrids[0] = [hybrids[0]]
        
        for hybrid in hybrids[0]:
            
            # EITHER, all chips
            #hybridoutnses = [hybrid.channels[c].outnse for c in range(len(hybrid.channels))]
            
            # OR, only the first chip
            channelsDict = {"all" : hybrid.chips[0].channels,
                            "stream0" : hybrid.chips[0].getStream(0),
                            "stream1" : hybrid.chips[0].getStream(1)}
            channels = channelsDict[hybrids[2]]
                            
            hybridoutnse = [channel.outnse for channel in channels]
            
            outnses.extend(hybridoutnse)
        
        if bins is None:
            outnseMin = int(min(outnses))
            outnseMax = int(max(outnses))
            n_bins = outnseMax + 5 - (outnseMin - 5)
            bins = np.linspace(min(outnses)-5, max(outnses)+5, n_bins)
        
        
        plt.hist(outnses, bins, label=hybrids[1]+", " + str(len(hybrids[0]))+ " tests" + {True:"", False:" "+hybrids[2]}[hybrids[2]=="all"], histtype="step")

    plt.title(title)
    plt.yscale(yscale)
    plt.xlabel("Outnse [mV/ENC]")
    plt.ylabel("# channels")
    plt.legend()

    plt.show()
    
    return fig

def plotRCClassified(hybrid, variable, streams = [0, 1], showStream0 = None, showStream1 = None,
                     showStats = False, zoomedIn = False, minValue = None, maxValue = None,
                     detectAnomalies = False, scoreChips = False, scoreType = "slope", figure = None,
                     title=None, showNow=True):
    """
    Plot channel input noise with classification coloring and labling, for a single hybrid.
    """
    
    if showStream0 is False:
        streams = [stream for stream in streams if stream != 0]
        print("Using showStream0 or showStream1 is deprecated. Please use stream = [list of streams to show].")
    if showStream1 is False:
        streams = [stream for stream in streams if stream != 1]
        print("Using showStream0 or showStream1 is deprecated. Please use stream = [list of streams to show].")
    if len(streams) < 1:
        raise Exception("Provided settings forces no streams to be shown.\nKwargs showStream0 and showStream1 are deprecated. Please use streams = [list of streams to show].")
    if not isinstance(streams, list):
        streams = list(streams)
    
    if variable not in ["innse", "outnse", "gain", "vt50"]:
        raise Exception("Please give variable as one of ['innse', 'outnse', 'gain', 'vt50']")

    nStreams = len(streams)
    if figure is None:
        fig, axs = plt.subplots(1, nStreams, figsize=(18, 4))
    else:
        fig, axs = figure
    if not isinstance(axs, np.ndarray) and not isinstance(axs, list):
        axs = [axs]
    comments = [parseCommentsList(channel.comment) for channel in hybrid.channels]
    channelColorDict = getChannelColorDict(comments)

    ylabel = {"innse" : "Input noise [ENC]",
              "outnse" : "Output noise [mV]",
              "gain" : "Gain [mv/fC]",
              "vt50" : "Vt50"}[variable]
    axisTitle = {"innse" : "Input noise",
              "outnse" : "Output noise",
              "gain" : "Gain",
              "vt50" : "Vt50"}[variable]

    channels = {}
    values = {}
    for stream in streams:
        channels[stream] = hybrid.getStream(stream)
        values[stream] = np.array({"innse" : [channel.innse for channel in channels[stream]],
                                   "outnse" : [channel.outnse for channel in channels[stream]],
                                   "gain" : [channel.gain for channel in channels[stream]],
                                   "vt50" : [channel.vt50 for channel in channels[stream]]}[variable])

    if maxValue is None:
        maxValue = max([max(values[stream]) for stream in values])
    if minValue is None:
        minValue = min([min(values[stream]) for stream in values])
    
    if detectAnomalies:
        anomalyDict = hybrid.detectAnomalies(variable)
    
    for s, stream in enumerate(streams):
        colors = np.array([channelColorDict[parseCommentsList(channel.comment)] for channel in channels[stream]], dtype=object)
        
        badChannelMask = [channel.badchannel for channel in channels[stream]]
        goodChannelMask = [not channel.badchannel for channel in channels[stream]]
        channelNumbers = np.array([channel.channelnumber for channel in channels[stream]])
        
        ax = axs[s]
        ax.scatter(channelNumbers[badChannelMask], values[stream][badChannelMask],
                   marker='s', s=3, color=colors[badChannelMask], zorder=1)
        ax.scatter(channelNumbers[goodChannelMask], values[stream][goodChannelMask],
                   marker='s', s=2, color=colors[goodChannelMask], zorder=-1)
        
        if not zoomedIn:
            ylimLower = minValue * 0.9
            ylimUpper =  min(maxValue * 1.1, 20000) # Make sure single insane high-value channels don't take over
            ax.set(ylim=[ylimLower, ylimUpper])
        ax.set_title(axisTitle + " " + {0 : "under", 1 : "away"}[stream])
        ax.set_xlabel("Channel #")
        ax.set_ylabel(ylabel)
        
        # Show statistics; mean and allowedSigma * standard deviation
        if showStats:
            for chip in hybrid.chips:
                means = {"gain" : chip.meanGain(stream=stream, countbadchannels=False),
                         "innse" : chip.meanInnse(stream=stream, countbadchannels=False),
                         "outnse": chip.meanOutnse(stream=stream, countbadchannels=False),
                         "vt50": chip.meanVt50(stream=stream, countbadchannels=False)}
                sigmas = {"gain" : chip.sigmaGain(stream=stream, countbadchannels=False),
                         "innse" : chip.sigmaInnse(stream=stream, countbadchannels=False),
                         "outnse": chip.sigmaOutnse(stream=stream, countbadchannels=False),
                         "vt50": chip.sigmaVt50(stream=stream, countbadchannels=False)}
                if means[variable] and sigmas[variable]:                    
                    xPoints = [chip.getStream(stream)[0].channelnumber, chip.getStream(stream)[-1].channelnumber]
                    
                    if True:#chip.badchip:
                        ylim = ax.get_ylim()
                        ax.text(xPoints[0]+10, ylim[0]*1.05, f"Sigma=\n{sigmas[variable]:.2f}")
                    
                    ax.plot(xPoints, [means[variable]]*2, '--', color='black', zorder=0)
                    if variable == "vt50":
                        ax.fill_between(xPoints, means[variable]-80, means[variable]+80,
                                        color='grey', alpha=0.1, zorder=0)
                    else:
                        ax.fill_between(xPoints, means[variable]-sigmas[variable] * chip.allowedSigmas[variable][stream],
                                        means[variable]+sigmas[variable] * chip.allowedSigmas[variable][stream], color='grey', alpha=0.1, zorder=0)
        ax.set(xlim=[channelNumbers[0], channelNumbers[-1]])
        ax.set(xticks=channelNumbers[::128])
        for x in ax.get_xticks():
            ax.axvline(x, 0, 1, linestyle='--', alpha=0.1)
        
        # Mark bad chips
        chipCommentPatchDict = {}
        for c, chip in enumerate(hybrid.chips):
            if chip.badchip:
                print("Chip", c, "is bad. Comments:")
                print(chip.comment)
                commentsToShow = []
                for comment in chip.comment:
                    if "BAD" in comment:
                        commentsToShow.append(comment)
                
                if len(commentsToShow) > 0:
                    import matplotlib.patches as patches
                    
                    for comment in commentsToShow:
                        hatch = {"BAD CHIP NOISE SIGMA" : "\\\\",
                                 "BAD CHIP GAIN SIGMA" : "//",
                                 "STREAM 0 ALL BAD" : "||",
                                 "STREAM 1 ALL BAD" : "--"}[comment]
                        color = {"BAD CHIP NOISE SIGMA" : "red",
                                 "BAD CHIP GAIN SIGMA" : "blue",
                                 "STREAM 0 ALL BAD" : "yellow",
                                 "STREAM 1 ALL BAD" : "yellow"}[comment]
                        ylims = ax.get_ylim()
                        corner = (c * 128, ylims[0])
                        width = 128
                        height = ylims[1] - ylims[0]
                        patch = patches.Rectangle(corner, width, height,
                                                  hatch=hatch, fill=None,
                                                  linewidth=0, alpha=0.4,
                                                  color=color, label=comment,
                                                  zorder=-2)
                        ax.add_patch(patch)
                        if comment not in chipCommentPatchDict.keys():
                            chipCommentPatchDict[comment] = patch

        # Show detected anomalies                        
        if detectAnomalies:
            y = ax.get_ylim()[1] * 0.98
            for n, x in enumerate(ax.get_xticks()[:-1]):
                if len(anomalyDict[0][n]) > 0:
                    anomalies = anomalyDict[0][n][0]
                    if len(anomalyDict[0][n]) > 1:
                        for anomaly in anomalyDict[0][n][1:]:
                            anomalies += "\n" + anomaly
                    ax.text(x+10, y, anomalies, fontsize="x-small", verticalalignment="top")
            
        # Show chip scores of type scoreType
        if scoreChips:
            from analysis.FeatureLibrary.FeatureScore import getFScores, getGradientScore
            import matplotlib.patches as patches
            
            for c, chip in enumerate(hybrid.chips):
                slope, skew = getFScores(chip, stream, variable)
                grad = getGradientScore(chip, stream)
                score = {"slope" : slope,
                         "skew" : skew,
                         "grad" : grad}[scoreType]
                
                # Generate score color map
                from matplotlib.colors import ListedColormap, Normalize
                from matplotlib.cm import ScalarMappable
                colorArray = np.array([[i/255, 128/255-np.abs(128-i)/255, 1-(i/255), 1] for i in range(256)])
                cmap = ListedColormap(colorArray)
                minScore = {"slope" : -80,
                            "skew" : -30,
                            "grad" : 0}[scoreType]
                maxScore = {"slope" : 80,
                            "skew" : 25,
                            "grad" : 2}[scoreType]
                norm = Normalize(minScore, maxScore)
                color = cmap(norm(score))
                alphaNorm = {"slope" : Normalize((maxScore+minScore)/2, maxScore),
                             "skew" : Normalize((maxScore+minScore)/2, maxScore),
                             "grad" : None}[scoreType]
                alpha = {"slope" : alphaNorm(abs(score)),
                         "skew" : alphaNorm(abs(score)),
                         "grad" : 0.8}[scoreType]
                
                ylims = ax.get_ylim()
                corner = (c * 128, ylims[0])
                width = 128
                height = ylims[1] - ylims[0]
                patch = patches.Rectangle(corner, width, height, linewidth=0, alpha=alpha, color=color, zorder=-3)
                ax.add_patch(patch)

            cbar = plt.colorbar(mappable=ScalarMappable(norm, cmap), ax=ax, label=scoreType + " score", orientation="horizontal")
            
    legendHandles = []
    uniqueComments = list(set(comments))
    if "OK" in uniqueComments:
        tempComments = ["OK"]
        for comment in uniqueComments:
            if comment != "OK":
                tempComments.append(comment)
        uniqueComments = tempComments
    for c, comment in enumerate(uniqueComments):
        legendHandles.append(Line2D([0], [0], marker='o', color='w',
                                    markerfacecolor=channelColorDict[comment],
                                    label=comment.replace(", ", "\n").replace("(UNBONDED)", "")))
    for chipComment in chipCommentPatchDict:
        legendHandles.append(chipCommentPatchDict[chipComment])
    axs[0].legend(handles=legendHandles, bbox_to_anchor=(1,1), fontsize=8)

    for ax in axs:
        ax.set_facecolor("whitesmoke")

    plt.subplots_adjust(hspace=0.5, wspace=0.5)
    if title:
        plt.suptitle(title)
    if showNow:
        plt.show()
    return fig, axs

# Classification coloring helper
def getChannelColorDict(comments):
    uniqueComments = list(set(comments))
    if os.path.isfile("channelColorDict.json"):
        with open("channelColorDict.json", "r") as f:
            channelColorDict = json.load(f)
    else:
        channelColorDict = {"OK" : "lightgrey"}

    nStoredColors = len(channelColorDict.keys()) - 1
    cmap = cm.get_cmap("Set1")
    
    for comment in uniqueComments:
        if nStoredColors >= len(cmap.colors):
            cmap = cm.get_cmap("tab20")
        
        colorDefined = False
        for key in channelColorDict:
            if comment == key:
                colorDefined = True
                break
        if not colorDefined:
            if nStoredColors >= len(cmap.colors):
                # Temporary fix to having "comments" that are actually combinations of lots of other comments
                # TODO: Pile channels with lots of problems into some general "bad" comment
                channelColorDict[comment] = "black"
            else:
                channelColorDict[comment] = cmap.colors[nStoredColors]
                nStoredColors += 1
        
    with open("channelColorDict.json", "w") as f:
        json.dump(channelColorDict, f, indent=2)

    return channelColorDict

# Classification comment helper
def getChannelClassificationComments(chip):
    for i in range(0,10):
        meanGain = chip.meanGain(countbadchannels=False)
        sigmaGain = chip.sigmaGain(countbadchannels=False)
        meanVt50 = chip.meanVt50(countbadchannels=False)
        sigmaVt50 = chip.sigmaVt50(countbadchannels=False)
        meanInnse = chip.meanInnse(countbadchannels=False)
        sigmaInnse = chip.sigmaInnse(countbadchannels=False)
        
        comments = [None] * len(chip.channels)
        for c, channel in enumerate(chip.channels):
            badChannel, commentsList = channel.classification(chip, strategy = "NathanR0RevisedIteration", meanGain = meanGain, sigmaGain = sigmaGain, meanVt50 = meanVt50, sigmaVt50 = sigmaVt50, meanInnse = meanInnse, sigmaInnse = sigmaInnse)
            comment = parseCommentsList(commentsList)
            if comment:
                comments[c] = comment
            else:
                comments[c] = "OK"
    return comments
    
def parseCommentsList(commentsList):
    
    if commentsList is None or commentsList == []:
        return ""
    if isinstance(commentsList, list):
        comments = commentsList[0]
        for comment in commentsList[1:]:
            comments += ", " + comment
    elif isinstance(commentsList, CommentHandler):
        commentsList = commentsList.commentList
        comments = commentsList[0]
        for comment in commentsList[1:]:
            comments += ", " + comment
    return comments

def plotRCAnomalies(chip, streams=[0, 1], windowSize=16, countbadchannels=False):
    skipStart = windowSize // 2
    skipEnd = windowSize - skipStart
    returns = []
    if not isinstance(streams, list):
        streams = [streams]
    for stream in streams:
        print(stream)
        channels = chip.getStream(stream)
        colorDict = {False : 'blue', True : 'grey'}
        colors = [colorDict[channel.badchannel] for channel in channels]
        chanNums = [channel.channelnumber for channel in channels]
        allInnses = [channel.innse for channel in channels]
        if countbadchannels:
            usedChanNums = chanNums
            innses = allInnses
        else:
            usedChanNums = [channel.channelnumber for channel in channels if not channel.badchannel]
            innses = [channel.innse for channel in channels if not channel.badchannel]
        means = []
        sigmas = []
        for c in range(len(innses) - windowSize):
            means.append(np.mean(innses[c:c+windowSize]))
            sigmas.append(np.std(innses[c:c+windowSize]))
        sigmaSigma = np.std(sigmas)
        meanMean = np.mean(means)
        
        sideMeans = (sum([mean-meanMean for mean in means[:len(means)//2]])/meanMean,
                     sum([mean-meanMean for mean in means[len(means)//2:]])/meanMean)
        
        fig, axs = plt.subplots(3,1, sharex=True, gridspec_kw={'height_ratios': [3,1,1]})
        axs[0].scatter(chanNums, allInnses, color=colors, marker='.')
        axs[0].set_ylabel("Input noise [ENC]")
        
        legendHandles = []
        comments = ["Good channel", "Bad channel"]
        bools = [False, True]
        for c, comment in enumerate(comments):
            legendHandles.append(Line2D([0], [0], marker='o', color='w',
                                        markerfacecolor=colorDict[bools[c]], label=comment))
        #axs[0].legend(handles=legendHandles, bbox_to_anchor=(1,1), fontsize=8)
        axs[0].legend(handles=legendHandles, loc='best', fontsize=8)
        
        axs[1].plot(usedChanNums[skipStart:-skipEnd], means, '.')
        axs[1].set_ylabel("Mean")
        
        axs[2].plot(usedChanNums[skipStart:-skipEnd], sigmas, '.')
        axs[2].set_xlabel("Channel #")
        axs[2].set_ylabel("Sigma")
        plt.subplots_adjust(hspace=0.1)
        plt.show()
        print("Stream", stream, "window sigma standard deviation:", sigmaSigma)
        
        returns.append((sigmaSigma, meanMean, (means[0], means[-1]), sideMeans))
    return returns

def plotClassificationStats(hybrids, title=None, xlabels=None, showNow=True, showType=False, yLimits=None):
    # Note the use of the variable name "hybrids" to be consistent in this file.
    # However, this function is probably only used with full modules.
    nHybrids = len(hybrids)
    figWidth = min(int(nHybrids / 50 * 12 + 8), 20)
    print("figWidth =", figWidth)
    fig, ax = plt.subplots(figsize=(figWidth, 8))
    
    # Gather all comments in hybrid set
    commentCounts = {}
    for h, hybrid in enumerate(hybrids):
        for channel in hybrid.channels:
            comment = str(channel.comment)
            if comment not in commentCounts.keys():
                commentCounts[comment] = [0 for _ in range(len(hybrids))]
            commentCounts[comment][h] += 1
        nChannels = len(hybrid.channels)
        for comment in commentCounts:
            commentCounts[comment][h] *= 100/nChannels

    # Plot bar for each hybrid
    bottom = np.array([0. for _ in range(len(hybrids))])
    channelColorDict = getChannelColorDict(list(commentCounts.keys()))
    for comment in sorted(commentCounts, reverse=True):
        if comment != "OK":
            color = channelColorDict[comment]
            ax.bar([x for x in range(len(hybrids))], commentCounts[comment],
                   label=comment, bottom=bottom, color=color, width=1.)
            bottom += commentCounts[comment]
    
    # Separate bars
    for x in range(len(hybrids) - 1):
        plt.axvline(x+.5, color="lightgrey")
    
    # Organize plot
    if xlabels:
        ax.set_xticks(list(range(len(hybrids))))
        ax.set_xticklabels(xlabels, rotation=90)
        plt.subplots_adjust(bottom=0.3)
    rightAdjust = min(figWidth / 20 * 0.5 + 0.2, 0.7)
    print("rightAdjust =", rightAdjust)
    plt.subplots_adjust(left=0.05, right=rightAdjust)
    ax.set_xlim([-.5, len(hybrids) - .5])
    if yLimits:
        ax.set_ylim(yLimits)
    else:
        ax.set_ylim([0., 5.])
    ax.set_ylabel("% of channels")
    plt.axhline(y=2., color="k", linestyle="--")
    
    # Annotate module types in plot if showType==True
    if showType == True:
        typeCounts = {}
        for hybrid in hybrids:
            if hybrid.subtype not in typeCounts.keys():
                typeCounts[hybrid.subtype] = 0
            typeCounts[hybrid.subtype] += 1
        print(typeCounts)
        x = 0
        
        topAxXticks = [0]
        for hybridType in list(typeCounts.keys())[:-1]:
            x += typeCounts[hybridType]
            topAxXticks.append(x)
            plt.axvline(x=x-.5, linestyle="-", color="k")
        topAx = ax.twiny()
        topAx.set_xlim(ax.get_xlim())
        topAx.set_xticks(topAxXticks)
        topAx.set_xticklabels([hybridType for hybridType in typeCounts])
        topAx.tick_params(axis="x", labelsize=12)

    # Mark bad hybrids
    for h, hybrid in enumerate(hybrids):
        if hybrid.badModule:
            ax.get_xticklabels()[h].set_color("red")
            faultString = ""
            for comment in hybrid.fault:
                if "2%" not in comment:
                    faultString += comment + ", "
            faultString = faultString[:-2]
            ylim = ax.get_ylim()
            ax.text(h-.1, (ylim[1]-ylim[0])*.95, faultString, rotation=90, verticalalignment="top")
            # Code for printing number of bad channels / total number of channels on bar
            #numChannels = len(hybrid.channels)
            #numBad = sum([channel.badchannel for channel in hybrid.channels])
            #ax.text(h-.1, (ylim[1]-ylim[0])*.1, str(numBad) + "/" + str(numChannels), rotation=90)
        
    
    # Reverse legend handles so the appear in the same order as the colors in the bars
    handles, labels = ax.get_legend_handles_labels()
    handles.reverse()
    labels.reverse()
    ax.legend(handles, labels, bbox_to_anchor=(1, 1))
    if title:
        plt.suptitle(title)
    
    if showNow:
        plt.show()
    return fig

def plotMisclassificationRate(subtype, unbondedHybrids=None, bondedHybrids=None, stream=1, datapath=None, verbose=False):
    
    filename = os.sep.join([".", "downloadScripts", "jsonFiles", subtype + "data.json"])
    if subtype == "R2H1":
        print("Note: using R2H0 unbonded data since DB doesn't use the R2H1 label.")
        filename = os.sep.join([".", "downloadScripts", "jsonFiles", "R2H0" + "data.json"])
    
    cuts = getCuts(subtype)
    
    bondStatuses = ["unbonded", "bonded"]
    hybrids = {}
    if not unbondedHybrids or not bondedHybrids:
        hybrids = dict(zip(bondStatuses, getHybridsFromIDFile(filename, datapath=datapath, verbose=verbose, onlySingle=True)))
    if unbondedHybrids:
        hybrids["unbonded"] = unbondedHybrids
    if bondedHybrids:
        hybrids["bonded"] = bondedHybrids
    outnses = {"unbonded" : [], "bonded" : []}
    for bondStatus in bondStatuses:
        for hybrid in hybrids[bondStatus]:
            channelDict = {"unbonded" : hybrid.channels,
                           "bonded" : hybrid.getStream(stream)}
            outnses[bondStatus].extend([channel.outnse for channel in channelDict[bondStatus] if not channel.badchannel])
        outnses[bondStatus] = np.array(outnses[bondStatus])
        mask = (outnses[bondStatus] > cuts[0]) & (outnses[bondStatus] < cuts[1])
        outnses[bondStatus] = outnses[bondStatus][mask]
        
    abort = False
    for bondStatus in ["unbonded", "bonded"]:
        if len(hybrids[bondStatus]) == 0:
            print("No", bondStatus, "hybrids for subtype", subtype + ". Cannot run misclassification plot.")
            abort = True
    if abort:
        return
        
    binMin = cuts[0]
    binMax = cuts[1]
    nBins = 200
    bins = np.linspace(binMin, binMax, nBins)
    binCounts = {}
    binEdges = {}
    binCenters = {}
    for bondStatus in outnses:
        binCounts[bondStatus], binEdges[bondStatus] = np.histogram(outnses[bondStatus], bins=bins)
        binCenters[bondStatus] = [(binEdges[bondStatus][i] + binEdges[bondStatus][i+1]) / 2 for i in range(len(binEdges[bondStatus])-1)]

    mean = {}
    sigma = {}
    popt = {}
    pcov = {}
    for bondStatus in outnses:
        mean[bondStatus] = np.mean(outnses[bondStatus])
        sigma[bondStatus] = np.std(outnses[bondStatus])
        popt[bondStatus], pcov[bondStatus] = curve_fit(Gauss, binCenters[bondStatus],
                                                       binCounts[bondStatus],
                                                       p0=[max(binCounts[bondStatus]),
                                                       mean[bondStatus],
                                                       sigma[bondStatus]])
    def UnbondedGauss(x):
        return Gauss(x, *popt['unbonded'])
    def BondedGauss(x):
        return Gauss(x, *popt['bonded'])

    fig, axs = plt.subplots(2, 1, figsize=(6,10))
    colors = {'unbonded' : 'b', 'bonded' : 'r'}
    for bondStatus in outnses:
        label = bondStatus + " (N = " + str(len(hybrids[bondStatus])) + ")"
        axs[0].hist(outnses[bondStatus], bins=bins, color=colors[bondStatus], alpha=0.3, label=label)
        axs[0].plot(binCenters[bondStatus], Gauss(binCenters[bondStatus], *popt[bondStatus]), '-x', color=colors[bondStatus])
    
    histLimits = (mean["unbonded"]+1*sigma["unbonded"], mean["bonded"]-1*sigma["bonded"])
    axs[0].set_xlim(histLimits[0], histLimits[1])
    axs[0].set_ylim(0, 100)
    axs[0].set_ylabel('# channels')
    axs[0].set_xlabel('Output noise')
    axs[0].legend()
    axs[0].set_title(subtype + " " + {0:"under", 1:"away"}[stream])

    import scipy.integrate as integrate
    
    limits = (mean["unbonded"]+1*sigma["unbonded"], mean["bonded"]-1*sigma["bonded"])
    unbondedCuts = np.linspace(limits[0], limits[1], int((limits[1]-limits[0])*100))
    misRate = {'unbonded' : [],
               'bonded' : []}
    functions = {'unbonded' : UnbondedGauss,
                 'bonded' : BondedGauss}
    for bondStatus in outnses:
        for cut in unbondedCuts:
            under, _ = integrate.quad(functions[bondStatus], 0, cut)
            over, _ = integrate.quad(functions[bondStatus], cut, 10)
            misRate[bondStatus].append(100 * min(under, over) / (over + under))
    
    # Figure out reasonably y limits based on where the intersect between the bonded/unbonded curves lies
    prevDiff = 1000000
    for closestIdx, (unbondedMisRate, bondedMisRate) in enumerate(zip(misRate["unbonded"], misRate["bonded"])):
        diff = np.abs(unbondedMisRate - bondedMisRate)
        if diff > prevDiff:
            closestIdx -= 1
            break
        prevDiff = diff
    
    yHighLimit = max(bondedMisRate*2, 0.05)
    
    axs[1].plot(unbondedCuts, misRate['unbonded'], '.', color=colors['unbonded'], label='unbonded')
    axs[1].plot(unbondedCuts, misRate['bonded'], '.', color=colors['bonded'], label='bonded')
    axs[1].set_ylabel('Misclassification %')
    axs[1].set_xlabel('Output noise unbonded cut')
    axs[1].set_ylim([0, yHighLimit])
    axs[1].grid(visible=True)
    axs[1].legend()
    axs[1].set_title("Misclassification rate")
    
    line = axs[1].axvline(unbondedCuts[closestIdx], 0, 1, alpha = 0.5, linestyle = "--")
    xlims = axs[1].get_xlim()
    text_xmove = (xlims[1] - xlims[0])*.035
    axs[1].text(unbondedCuts[closestIdx]-text_xmove, axs[1].get_ylim()[1]*.85, f"{unbondedCuts[closestIdx]:.2f}", rotation="vertical", color=line.get_color())
    
    plt.subplots_adjust(hspace=0.3)
    return fig
    
def Gauss(x, a, x0, sigma):
    return a * np.exp (-(x - x0)**2 / (2 * sigma**2))