from metadataHelpers import getItkdbClient

client = getItkdbClient()

hybridSN = "20USEH00000250"

hybridComponent = client.get("getComponent", json={"component" : hybridSN})

ABCStarVersion = None
HCCStarVersion = None
for child in hybridComponent["children"]:
    if child["component"]:
        if child["componentType"]["code"] == "ABC":
            ABCStarVersion = child["type"]["code"]
        if child["componentType"]["code"] == "HCC":
            HCCStarVersion = child["type"]["code"]
    if ABCStarVersion and HCCStarVersion:
        break

print(ABCStarVersion, HCCStarVersion)