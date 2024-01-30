import numpy as np

def getFScores(chip, stream, variable):
    channels = [channel for channel in chip.getStream(stream) if not channel.badchannel]
    leftChannels = channels[:len(channels)//2]
    rightChannels = channels[len(channels)//2:]
    mean = {"outnse" : chip.meanOutnse,
            "innse"  : chip.meanInnse,
            "gain"   : chip.meanGain}[variable](stream=stream, countbadchannels=False)
    sLeft = 0
    sRight = 0

    values = [{"outnse" : channel.outnse,
               "innse"  : channel.innse,
               "gain"   : channel.gain}[variable] for channel in leftChannels[-1:0:-1]]
    xs = [x / len(leftChannels) for x in range(len(leftChannels))]
    ys = [y - mean for y in values]
    yMean = np.mean(np.abs(ys))
    ys = np.array(ys) / yMean
    ws = [x * y for x, y in zip(xs, ys)]
    sLeft = sum(ws)
    
    values = [{"outnse" : channel.outnse,
               "innse"  : channel.innse,
               "gain"   : channel.gain}[variable] for channel in rightChannels]
    xs = [x / len(rightChannels) for x in range(len(rightChannels))]
    ys = [y - mean for y in values]
    yMean = np.mean(np.abs(ys))
    ys = np.array(ys) / yMean
    ws = [x * y for x, y in zip(xs, ys)]
    sRight = sum(ws)
    
    slopeScore = sLeft - sRight
    skewScore = sLeft + sRight

    return (slopeScore, skewScore)

def getGradient(vector, step):
    grad = [None] * step
    for p1, p2 in zip(vector[:-2*step], vector[step*2:]):
        grad.append((p2 - p1) / (2 * step))
    grad.extend([None] * step)
    gradSum = 0
    for element in grad:
        if element is not None:
            gradSum += np.abs(element)
    return grad, gradSum

def getGradientScore(chip, stream, step=5, windowSize=16):
    values = [channel.outnse for channel in chip.getStream(stream) if not channel.badchannel]
    windowMeans = []
    for i in range(windowSize//2, len(values)-windowSize//2):
        windowValues = [value for value in values[i-windowSize//2:i+windowSize//2]]
        windowMeans.append(sum([value for value in windowValues])/len(windowValues))
    _, gradSum = getGradient(windowMeans, step)
    return gradSum