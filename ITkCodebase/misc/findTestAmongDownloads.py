import json, glob, sys

def findTest(serialNumber, runNumber):
    hits = []
    jsonFiles = glob.glob("./data/*.json")
    for jsonFile in jsonFiles:
        with open(jsonFile, "r") as f:
            js = json.load(f)
        if js["components"][0]["serialNumber"] == serialNumber:
            if js["runNumber"].split("-")[0] == runNumber:
                hits.append(jsonFile)
    if len(hits) > 0:
        for hit in hits:
            print(hit)
    else:
        print("No match found for sn", serialNumber, "and run number", runNumber)

if __name__ == "__main__":
    args = sys.argv[1:]
    print(findTest(args[0], args[1]))