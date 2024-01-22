"""
Script to find response curve tests before and after wire bonding to the sensor

For unbonded classification studies
"""

import itkdb
import sys
import os
import datetime
import json

#Potential TODO: rewrite to create folders per module type/serial number/some other organization

#Export access codes in bash with e.g.
#>>>export ITKDB_ACCESS_CODE1=mycode123
#Do not put it in any code
def downloadRCData(subtype, datapath):
    user = itkdb.core.User(accessCode1=os.environ['ITKDB_ACCESS_CODE1'], accessCode2=os.environ['ITKDB_ACCESS_CODE2'])
    user.authenticate()
    client = itkdb.Client(user=user)

    components = client.get('listComponents',json={'project': 'S','subproject':'SE', 'componentType':"HYBRID_ASSEMBLY", 'currentStage':'ON_MODULE', 'type':subtype})

    serialnumber = []

    for page in components.pages:
        for item in page['pageItemList']:
            sn = item['serialNumber']
            print(sn)
            serialnumber.append(sn)

    testpairs = []

    unbondedtestids = []
    bondedtestids = []
    
    added = 0

    #Temporary example, one single R1H0 STAR Hybrid Assembly
    #component_serNum = '20USEH20000015'
    #Temporary example, one single R0H0 STAR Hybrid Assembly
    #component_serNum = '20USEH00000217'
    for component_serNum in serialnumber:
        print("\n ****** \nFinding Hybrid Star Assembly component with serial number: " + component_serNum)
        myComp = client.get('getComponent', json={'component' : component_serNum})

        on_module = False
        on_module_dateTime = None


        for stage in myComp['stages']:
            if stage['code'] == "ON_MODULE":
                on_module = True
                #Remove trailing 'Z' in datetime string
                on_module_dateTime = datetime.datetime.fromisoformat(stage['dateTime'][:-1])

        print("Wire bonded to sensor: " + str(on_module))
        print("Time for module assembly: " + str(on_module_dateTime))

        #if not on_module:
        #   ignore this hybrid

        rc_hybrid_test = False
        rc_hybrid_testid = ""
        rc_module_test = False
        rc_module_testid = ""

        print("Response curve tests:")
        print("Note: includes 3 point gain, which is identical but is taken with just 3 different charges.")
        for test in myComp['tests']:
            if test['code'] == 'RESPONSE_CURVE_PPA':
                for testRun in test['testRuns']:
                    print("\nFound response curve")
                    #Remove trailing 'Z' in datetime string
                    #time = datetime.datetime.fromisoformat(testRun['date'][:-1])
                    #print(time)
                    testid = testRun['id']
                    if os.path.exists(datapath+"/"+str(testid)+".json"):
                        print("testid "+ testid + " already exists.")
                        continue
                    
                    print("testid: " + testid)
                    #Download test results
                    data = client.get("getTestRun", json={"testRun":testid})
                    print("Test run number: " +str(data['runNumber']))

                    chargepoints = 0
                    for prop in data['properties']:
                        try:
                            chargepoints = len(prop['value']['points'])
                        except: 
                            pass
                    print("Number of charge points:", chargepoints)
                    if chargepoints == 3:
                        print("Ignored test since it is a three point gain measurement")
                        continue

                    added += 1

                    testedAtStage = data['components'][0]['testedAtStage']['code']
                    print("Tested at stage: " + testedAtStage)

                    if testedAtStage == "ON_MODULE":
                        rc_module_test = True
                        rc_module_testid = testid
                        bondedtestids.append(rc_module_testid)
                    if testedAtStage == "FINISHED_HYBRID" or testedAtStage == "WIRE_BONDING":
                        rc_hybrid_test = True
                        rc_hybrid_testid = testid
                        unbondedtestids.append(rc_hybrid_testid)

                    #Download test results

                    file = open(datapath+"/"+str(testid)+".json", "w")
                    json.dump(data,file)
                    file.close()
        
        # TODO: Does testpairs actually work? It seems like if there are many tests, this breaks down
        if rc_hybrid_test and rc_module_test:
            testpairs.append([rc_hybrid_testid, rc_module_testid])

    print("\n ******************* \n Number of hybrids with unbonded and bonded response curve tests: " + str(len(testpairs)))
    print(testpairs)
    print("Bonded test ids:")
    print(bondedtestids)
    print("Unonded test ids:")
    print(unbondedtestids)
    print("Added", added, "new test ids.")
    return added

if __name__ == "__main__":
    if len(sys.argv) > 1:
        subtype = sys.argv[1:]
        print("Looking for subtype:", subtype)
        downloadRCData(subtype)
    else:
        subtype=input("Please specify subtype: ")
        print("Looking for subtype:", subtype)
        downloadRCData(subtype)