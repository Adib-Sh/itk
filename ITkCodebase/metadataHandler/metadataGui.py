import tkinter as tk
import json
from tkinter import ttk
from metadataHelpers import getMetadataKeys, getModuleTypes, getTestTuples, getModulesForClassification

import sys, os
sys.path.append(os.getcwd())
from parsers.RCparsers import parseRC, parseJsonRC
from plots.ResponseCurvePlots import plotRCHistograms, plotRCCycleMeans
from plots.ResponseCurvePlots import plotClassificationStats, plotRCClassified

def plotResults():
    hybrids = []
    print("\nParsing...")
    for result, _ in testTuples:
        hybrids.append(parseRC(result))
    print("Plotting results.\n")
    criteriaToDisplay = {}
    for key in criteria:
        if criteria[key] != "Any":
            criteriaToDisplay[key] = criteria[key]
    plotRCHistograms(hybrids, variable=variableToPlot, metadata=criteriaToDisplay)

def plotClassifications():
    # Plots classification stats for modules based on the selected criteria,
    # WITH THE EXCEPTION that it plots per module, i.e., for all hybrid types
    # on that module, so criteria["HybridType"] does not affect this plot.
    
    modules = []
    print("\nParsing and classifying...")
    moduleType = criteria["ModuleType"]
    moduleSNs = []
    for _, metadata in testTuples:
        moduleSNs.append(metadata["ModuleSN"])
    modules, moduleSNsUsed = getModulesForClassification(moduleType, criteria)
    title = criteria["ModuleType"] + " channel classification"
    plotClassificationStats(modules, title=title, xlabels=moduleSNsUsed)
    
def plotCycle():
    hybrids = []
    print("\nParsing...")
    for result, _ in testTuples:
        hybrids.append(parseRC(result))
    xlabels = [metadata["Timestamp"][:-5] for _, metadata in testTuples]
    print("Plotting result means.\n")
    title = criteria["ModuleSN"] + " " + criteria["ModuleType"] + criteria["HybridType"]
    plotRCCycleMeans(hybrids, variable=variableToPlot, title=title, xlabels=xlabels)
    
def plotSelected():
    result = resultsList.get(resultsList.curselection())
    filename = result.split("/")[-1]
    hybrid = parseRC(result)
    criteriaToDisplay = {}
    for key in criteria:
        if criteria[key] != "Any":
            criteriaToDisplay[key] = criteria[key]
    plotRCHistograms(hybrid, variable=variableToPlot, metadata=criteriaToDisplay, title=filename)

def plotSelectedClassified():
    result = resultsList.get(resultsList.curselection())
    _, metadata = testTuples[resultsList.curselection()[0]]
    
    peakMasking = False
    if metadata["ModuleType"][:2] in ["R4", "R5"]:
        peakMasking = False
    
    hybrid = parseJsonRC(result, peakMasking=peakMasking)
    hybrid.subtype = metadata["ModuleType"] + metadata["HybridType"]
        
    hybrid.classification(strategy="TypeSpecific")
    title = metadata["ModuleType"] + metadata["HybridType"] + " " + metadata["HybridSN"] + " on module " + metadata["ModuleSN"]
    plotRCClassified(hybrid, variable=variableToPlot, title=title, showStats=False)
    
def showMetadata(event):
    if len(testTuples) > 0:
        selectedTest = testTuples[resultsList.curselection()[0]]
        filename = selectedTest[0]
        label.config(text=f"Filename of selected test: {filename}")
    updateFields()

def commitMetadata():
    selectedTest = testTuples[resultsList.curselection()[0]]
    filename = selectedTest[0]
    metadataFilename = selectedTest[0][:selectedTest[0].rfind("/")+1] + "metadata.json"
    print(metadataFilename)
    label.config(text=f"Updating metadata of test {filename}")
    print(f"Updating metadata of test {filename}")
    print(f"in metadata file {metadataFilename}")
    updatedMetadata = {}
    print(f"{'Key':20}{'Old value':25}{'New value':25}")
    for key in metadataFields:
        updatedMetadata[key] = metadataFields[key].var.get()
        color = '\33[0m'
        if selectedTest[1][key] != updatedMetadata[key]:
            color = '\33[92m'
        print(f"{color}{key:20}{selectedTest[1][key]:25}{updatedMetadata[key]:25}\33[0m")
    
    with open(metadataFilename, "r") as f:
        storedTestMetadata = json.load(f)
    dataPath = "../data/PRR/"
    moduleSN = storedTestMetadata["ModuleSN"]
    if not storedTestMetadata["HalfModuleSN"] == "N/A":
        moduleSN = storedTestMetadata["HalfModuleSN"]
    moduleMetadataPath = dataPath + storedTestMetadata["ModuleType"] + "/" + moduleSN + "/"
    with open(moduleMetadataPath + "moduledata.json", "r") as f:
        storedModuleMetadata = json.load(f)
    for key in updatedMetadata:
        if key in storedTestMetadata.keys():
            storedTestMetadata[key] = updatedMetadata[key]
        elif key in storedModuleMetadata.keys():
            storedModuleMetadata[key] = updatedMetadata[key]
    with open(metadataFilename, "w") as f:
        json.dump(storedTestMetadata, f)
    with open(moduleMetadataPath + "moduledata.json", "w") as f:
        json.dump(storedModuleMetadata, f)
    print()
    updateOptions()

def moduleTypeSelected(event):
    global criteria, dropdownMenus, dropdownVars
    criteria["ModuleType"] = dropdownVars["ModuleType"].get()
    dropdownMenus["HybridType"]['values'] = moduleTypes[criteria["ModuleType"]]
    dropdownVars["HybridType"].set(moduleTypes[criteria["ModuleType"]][0])
    updateOptions()
    selection = criteria["ModuleType"]
    nResults = len(testTuples)
    label.config(text=f"Selected: {selection}. # results: {nResults}")

def hybridTypeSelected(event):
    global criteria
    criteria["HybridType"] = dropdownVars["HybridType"].get()
    updateOptions()
    selection = criteria["HybridType"]
    nResults = len(testTuples)
    label.config(text=f"Selected: {selection}. # results: {nResults}")
    
def populateDropdowns():
    # Reset metadata options based on new selection criteria
    for key in metadataOptions:
        metadataOptions[key] = ["Any"]    
    # Populate new metadata options
    for _, metadata in testTuples:
        for key in metadataOptions:
            if metadata[key] not in metadataOptions[key]:
                metadataOptions[key].append(metadata[key])

def updateDropdowns():
    for key in metadataOptions:
        dropdownMenus[key].update()
    
def updateOptions(refresh=True):
    global testTuples
    testTuples = getTestTuples(criteria)
    if refresh:
        populateDropdowns()
        updateDropdowns()
    updateResults()
    showMetadata(None)

def updateResults():
    global resultsList, testTuples
    resultsList.delete(0, tk.END)
    for result, _ in testTuples:
        resultsList.insert(tk.END, result)
    #if len(testTuples) > 0:
    resultsList.selection_set(0)

def updateFields():
    if len(testTuples) > 0:
        for key in metadataFields:
            metadataFields[key].var.set(testTuples[resultsList.curselection()[0]][1][key])
        for key in staticFields:
            staticFields[key].var.set(testTuples[resultsList.curselection()[0]][1][key])
    else:
        for key in metadataFields:
            metadataFields[key].var.set("")
        for key in staticFields:
            staticFields[key].var.set("")

def selectVariable(event):
    global variableToPlot
    variableToPlot = variableDropdownVar.get()

class DropdownMenu():
    def __init__(self, frame, key, options):
        self.options = options
        self.key = key
        self.var = tk.StringVar(value=options[0])
        self.header = tk.Label(frame, text=key)
        self.menu = ttk.Combobox(frame, textvariable=self.var, values=self.options)
        self.menu.bind("<<ComboboxSelected>>", self.selected)
    def pack(self):
        self.header.pack(padx=10, pady=2)
        self.menu.pack(padx=10, pady=2)
    def selected(self, event, refresh=False):
        global criteria
        selection = self.var.get()
        criteria[self.key] = selection
        updateOptions(refresh=refresh)
        nResults = len(testTuples)
        label.config(text=f"Selected: {selection}. # results: {nResults}")
    def update(self):
        self.menu["values"] = metadataOptions[self.key]
        if self.var.get() not in self.menu["values"]:
            self.var.set(self.menu["values"][0])
            print("Setting", self.key, "to", self.var.get())
            self.selected(None, refresh=True)

class MetadataField():
    def __init__(self, frame, key):
        self.key = key
        self.var = tk.StringVar()
        self.header = tk.Label(frame, text=key)
        self.header.pack(padx=10, pady=2)
        self.field = tk.Entry(frame, textvariable=self.var)
        self.field.pack(padx=10, pady=2)

class MetadataStaticField():
    def __init__(self, frame, key):
        self.key = key
        self.var = tk.StringVar()
        self.header = tk.Label(frame, text=key)
        self.header.pack(padx=10, pady=2)
        self.field = tk.Label(frame, textvariable=self.var)
        self.field.pack(padx=10, pady=2)

root = tk.Tk()
root.title("RESCUME - Response Curve Metadata")

label = tk.Label(root, text="")
label.pack(padx=20, pady=20)

buttonFrame = tk.Frame(root)
buttonFrame.pack(side=tk.TOP, padx=20, anchor="n")
selectionFrame = tk.Frame(root)
selectionFrame.pack(side=tk.LEFT, padx=20, anchor="n")
selectionFrame2 = tk.Frame(root)
selectionFrame2.pack(side=tk.LEFT, padx=20, anchor="n")
resultsFrame = tk.Frame(root)
resultsFrame.pack(side=tk.LEFT, padx=20, anchor="n")
textFieldFrame = tk.Frame(root)
textFieldFrame.pack(side=tk.LEFT, padx=20, anchor="n")

plotButton = tk.Button(buttonFrame, text="Plot results", command=plotResults)
plotButton.pack(side=tk.LEFT, padx=10, pady=10)

plotClassificationsButton = tk.Button(buttonFrame, text="Plot classifications", command=plotClassifications)
plotClassificationsButton.pack(side=tk.LEFT, padx=10, pady=10)

variables = ["innse", "outnse", "gain", "vt50"]
variableToPlot = variables[0]
variableDropdownVar = tk.StringVar(value=variableToPlot)
selectVariableDropdown = ttk.Combobox(buttonFrame, textvariable=variableDropdownVar, values=variables)
selectVariableDropdown.bind("<<ComboboxSelected>>", selectVariable)
selectVariableDropdown.pack(side=tk.LEFT, padx=10, pady=10)

plotCycleButton = tk.Button(buttonFrame, text="Plot means of results", command=plotCycle)
plotCycleButton.pack(side=tk.LEFT, padx=10, pady=10)

plotSelectedButton = tk.Button(buttonFrame, text="Plot selected", command=plotSelected)
plotSelectedButton.pack(side=tk.LEFT, padx=10, pady=10)

plotSelectedButton = tk.Button(buttonFrame, text="Plot selected classified", command=plotSelectedClassified)
plotSelectedButton.pack(side=tk.LEFT, padx=10, pady=10)

updateMetadataButton = tk.Button(buttonFrame, text="Commit updated metadata", command=commitMetadata)
updateMetadataButton.pack(side=tk.LEFT, padx=10, pady=10)

metadataKeys = getMetadataKeys(metadataType="all")
moduleTypes = getModuleTypes()
moduleTypeOptions = list(moduleTypes.keys())

criteria = dict(zip(metadataKeys, ["Any"]*len(metadataKeys)))
criteria["ModuleType"] = moduleTypeOptions[0]
criteria["HybridType"] = moduleTypes[criteria["ModuleType"]][0]

metadataOptions = {}
metadataOptions["HalfModuleType"] = ["Any"]
for key in metadataKeys[3:]:
    metadataOptions[key] = ["Any"]
    
testTuples = getTestTuples(criteria)
populateDropdowns()

dropdownVars = {}
dropdownMenus = {}
# Module type dropdown
dropdownVars["ModuleType"] = tk.StringVar(value = criteria["ModuleType"])
moduleTypeHeader = tk.Label(selectionFrame, text="Module type:")
moduleTypeHeader.pack(padx=10, pady=2)
dropdownMenus["ModuleType"] = ttk.Combobox(selectionFrame, textvariable=dropdownVars["ModuleType"],
                        values=moduleTypeOptions)
dropdownMenus["ModuleType"].bind("<<ComboboxSelected>>", moduleTypeSelected)
dropdownMenus["ModuleType"].pack(padx=10, pady=2)

# Hybrid type dropdown
dropdownVars["HybridType"] = tk.StringVar(value = criteria["HybridType"])
hybridTypeHeader = tk.Label(selectionFrame, text="Hybrid type:")
dropdownMenus["HybridType"] = ttk.Combobox(selectionFrame, textvariable=dropdownVars["HybridType"],
                        values=moduleTypes[criteria["ModuleType"]])
dropdownMenus["HybridType"].bind("<<ComboboxSelected>>", hybridTypeSelected)

# Remaining dropdowns
for k, key in enumerate(metadataOptions):
    frame = selectionFrame if k < 14 else selectionFrame2
    dropdownMenus[key] = DropdownMenu(frame, key, metadataOptions[key])

# Pack dropdowns in correct order
dropdownMenus["HalfModuleType"].pack()
hybridTypeHeader.pack(padx=10, pady=2)
dropdownMenus["HybridType"].pack(padx=10, pady=2)
for key in list(metadataOptions.keys())[1:]:
    dropdownMenus[key].pack()

nStaticFields = 9
# Text fields
metadataFields = {}
for key in metadataKeys[nStaticFields:]:
    metadataFields[key] = MetadataField(textFieldFrame, key)

# Labels showing static metadata
staticFields = {}
for key in metadataKeys[:nStaticFields]:
    staticFields[key] = MetadataStaticField(selectionFrame2, key)

# Listbox for test results
resultsList = tk.Listbox(resultsFrame, width=50, height=45, exportselection=False)
resultsList.pack(padx=10, pady=10)
resultsList.bind("<<ListboxSelect>>", showMetadata)
updateResults()

updateFields()

root.mainloop()