import unbondedClassification

with open("../Helpers/subtypes.txt", 'r') as f:
    subtypes = f.read().split(',')

for subtype in subtypes:
    filename = "../Helpers/jsonFiles/" + subtype + "data.json"
    unbondedClassification.main(filename)