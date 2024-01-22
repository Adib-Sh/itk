from downloadScripts.downloadRCData import downloadRCData

pfxs = ['R' + str(i) for i in range(6)]
sfxs = ['H' + str(i) for i in range(4)]

addedTotal = 0
addedDict = {}

for pfx in pfxs:
    for sfx in sfxs:
        subtype = pfx+sfx
        print("==== Looking for", subtype, "====")
        count = downloadRCData(subtype)
        addedTotal += count
        if count > 0:
            addedDict[subtype] = count


print()
for subtype in addedDict:
    print(subtype, "-", addedDict[subtype], "new test ids.")

print("In total, added", addedTotal, "new test ids.")