from metadataHelpers import getItkdbClient

client = getItkdbClient()

hybridSN = "20USEH00000250"

hybridComponent = client.get("getComponent", json={"component" : hybridSN})

parents = hybridComponent["parents"]
parentSN = None
for parent in parents:
    if parent["componentType"]["code"] == "MODULE":
        parentSN = parent["component"]["serialNumber"]
        break
if not parentSN:
    print("Could not get parent module from database.")

print(parentSN)