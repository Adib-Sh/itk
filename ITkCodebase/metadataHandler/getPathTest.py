def getPath(value, dct):
    if value == dct:
        return value

    if isinstance(dct, dict):
        for key in dct:
            nextStep = getPath(value, dct[key])
            if nextStep == value:
                return [key]
            elif nextStep:
                return [key] + nextStep
        return False

    if isinstance(dct, list):
        for element in range(len(dct)):
            nextStep = getPath(value, dct[element])
            if nextStep == value:
                return [element]
            elif nextStep:
                return [element] + nextStep
        return False
    
    return False

def getValueByKey(wantedKey, dct):
    if isinstance(dct, dict):
        for key in dct:
            print("   ", key)
            if key == wantedKey:
                return dct[key]
            nextStep = getValueByKey(wantedKey, dct[key])
            if nextStep:
                return nextStep
    
    if isinstance(dct, list):
        for element in range(len(dct)):
            print("   ", element)
            nextStep = getValueByKey(wantedKey, dct[element])
            if nextStep:
                return nextStep
    
    return False