import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def none_zero(lst):
    return [0 if value is None else value for value in lst]


path = os.getcwd()
class get_data():
    def __init__(self,file):
        self.path = os.getcwd()
        self.rc_file = self.path + file

    
    def test_env_data(self):
        with open(self.rc_file, "r") as file:
            data = json.load(file)
            
        return data
    
    
#Read Test Data
file = "/results/20240404/output20240404/AMAC_data_2024-04-04.json"
#file = "\\results\\20240404\\output20240404\\test_data_2024-04-04.json"
reader = get_data(file)
data = reader.test_env_data()


#Data for plots

#Chuck 4 data
all_results = {}
for test_key, test_data in data.items():
    # Extract DP.1 and timestamps from the test data
    timestamps = test_data.get("results", {}).get("timestamps", [])
    Iin = test_data.get("results", {}).get("Iin", [])
    Iout = test_data.get("results", {}).get("Iout", [])
    Iin_hi = test_data.get("results", {}).get("Iin_Hi", [])
    Iout_hi = test_data.get("results", {}).get("Iout_Hi", [])
    Iin_lo = test_data.get("results", {}).get("Iin_Lo", [])
    Iout_lo = test_data.get("results", {}).get("Iout_Lo", [])
    Vin = test_data.get("results", {}).get("Vin", [])
    Vout = test_data.get("results", {}).get("Vout", [])
    NTCx = test_data.get("results", {}).get("NTCx", [])
    NTCy = test_data.get("results", {}).get("NTCy", [])
    NTCpb = test_data.get("results", {}).get("NTCpb", [])
    
    
    
    # Add DP.1 and timestamps to the results dictionary
    all_results[test_key] = {
        "time": timestamps,
        "Iin": Iin,
        "Iout": Iout,
        "Iin_Hi": Iin_hi,
        "Iout_Hi": Iout_hi,
        "Iin_Lo": Iin_lo,
        "Iout_Lo": Iout_lo,
        "Vin": Vin,
        "Vout": Vout,
        "NTCx": NTCx,
        "NTCy": NTCy,
        "NTCpb": NTCpb,
        }



#Plots
# Creating subplots
# Plotting the first set of data

test_keys = list(all_results.keys())  # Get the keys of all tests
num_tests = len(test_keys)

# Assuming there are at least 8 tests
for i in range(0, num_tests, 3):  # Loop through test keys by increments of 3
    # Extract data for the current tests
    test_key_1 = test_keys[i]
    test_data_1 = all_results[test_key_1]
    test_key_2 = test_keys[i + 1]
    test_data_2 = all_results[test_key_2]
    test_key_3 = test_keys[i + 2]
    test_data_3 = all_results[test_key_3]

    # Extract time and sensor data for each test
    time_labels_1 = [datetime.fromisoformat(t).strftime('%H:%M:%S') for t in test_data_1["time"]]
    time_labels_1 = time_labels_1[:-1]
    Iin_1 = test_data_1["Iin"]
    val_range_1 = int(len(Iin_1)/2)+1
    Iin_1 = Iin_1[val_range_1:]
    Iout_1 = test_data_1["Iout"]
    Iout_1 = Iout_1[val_range_1:]
    Iin_hi_1 = test_data_1["Iin_Hi"]
    Iin_hi_1 = Iin_hi_1[val_range_1:]
    Iout_hi_1 = test_data_1["Iout_Hi"]
    Iout_hi_1 = Iout_hi_1[val_range_1:]
    Iin_lo_1 = test_data_1["Iin_Lo"]
    Iin_lo_1 = Iin_lo_1[val_range_1:]
    Iout_lo_1 = test_data_1["Iout_Lo"]
    Iout_lo_1 = Iout_lo_1[val_range_1:]
    Vin_1 = test_data_1["Vin"]
    Vin_1 = Vin_1[val_range_1:]
    Vout_1 = test_data_1["Vout"]
    Vout_1 = Vout_1[val_range_1:]
    NTCx_1 = test_data_1["NTCx"]
    NTCx_1 = NTCx_1[val_range_1:]
    NTCy_1 = test_data_1["NTCy"]
    NTCy_1 = NTCy_1[val_range_1:]
    NTCpb_1 = test_data_1["NTCpb"]
    NTCpb_1 = NTCpb_1[val_range_1:]
    
    time_labels_3 = [datetime.fromisoformat(t).strftime('%H:%M:%S') for t in test_data_3["time"]]
    time_labels_3 = time_labels_3[:-1]
    Iin_3 = test_data_3["Iin"]
    #val_range_3 = int(len(Iin_3)/2)-1
    Iin_3 = Iin_3[:-1]
    Iout_3 = test_data_3["Iout"]
    Iout_3 = Iout_3[:-1]
    Iin_hi_3 = test_data_3["Iin_Hi"]
    Iin_hi_3 = Iin_hi_3[:-1]
    Iout_hi_3 = test_data_3["Iout_Hi"]
    Iout_hi_3 = Iout_hi_3[:-1]
    Iin_lo_3 = test_data_3["Iin_Lo"]
    Iin_lo_3 = Iin_lo_3[:-1]
    Iout_lo_3 = test_data_3["Iout_Lo"]
    Iout_lo_3 = Iout_lo_3[:-1]
    Vin_3 = test_data_3["Vin"]
    Vin_3 = Vin_3[:-1]
    Vout_3 = test_data_3["Vout"]
    Vout_3 = Vout_3[:-1]
    NTCx_3 = test_data_3["NTCx"]
    NTCx_3 = NTCx_3[:-1]
    NTCy_3 = test_data_3["NTCy"]
    NTCy_3 = NTCy_3[:-1]
    NTCpb_3 = test_data_3["NTCpb"]
    NTCpb_3 = NTCpb_3[:-1]
    
    time_labels_2 = [datetime.fromisoformat(t).strftime('%H:%M:%S') for t in test_data_2["time"]]
    time_labels_2 = time_labels_2[:-1]
    Iin_2 = test_data_2["Iin"]
    val_range_2 = int(len(Iin_2)/2)+1
    Iin_2 = Iin_2[val_range_2:]
    Iout_2 = test_data_2["Iout"]
    Iout_2 = Iout_2[val_range_2:]
    Iin_hi_2 = test_data_2["Iin_Hi"]
    Iin_hi_2 = Iin_hi_2[val_range_2:]
    Iout_hi_2 = test_data_2["Iout_Hi"]
    Iout_hi_2 = Iout_hi_2[val_range_2:]
    Iin_lo_2 = test_data_2["Iin_Lo"]
    Iin_lo_2 = Iin_lo_2[val_range_2:]
    Iout_lo_2 = test_data_2["Iout_Lo"]
    Iout_lo_2 = Iout_lo_2[val_range_2:]
    Vin_2 = test_data_2["Vin"]
    Vin_2 = Vin_2[val_range_2:]
    Vout_2 = test_data_2["Vout"]
    Vout_2 = Vout_2[val_range_2:]
    NTCx_2 = test_data_2["NTCx"]
    NTCx_2 = NTCx_2[val_range_2:]
    NTCy_2 = test_data_2["NTCy"]
    NTCy_2 = NTCy_2[val_range_2:]
    NTCpb_2 = test_data_2["NTCpb"]
    NTCpb_2 = NTCpb_2[val_range_2:]
    
    
    
    # Plotting
    plt.figure(figsize=(25, 12))  # Adjust figure size as needed
    plt.suptitle('Plot of test interval AMAC electrical data (2024.04.04)', fontsize=25)
    
    # First subplot (Iin)
    plt.subplot(4, 3, i + 1)
    plt.plot(time_labels_1, Iin_1, 'g-', label=test_key_1)
    plt.ylabel('I in (nA)')
    #min_val = min(x for x in Iin_1 if x is not None)-2
    #max_val = max(x for x in Iin if x is not None)+2
    #plt.ylim(min_val, max_val)
    plt.title("LTRT COLD TEST 1")
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 2)
    plt.plot(time_labels_3, Iin_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.title("IDLE")
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 3)
    plt.plot(time_labels_2, Iin_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.title("LTRT COLD TEST 2")
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])


    # Second subplot (Iout)
    plt.subplot(4, 3, i + 4)
    plt.plot(time_labels_1, Iout_1, 'g-', label=test_key_1)
    plt.ylabel('I out (nA)')
    #min_val = min(x for x in Iin_1 if x is not None)-2
    #max_val = max(x for x in Iin if x is not None)+2
    plt.ylim(760, 860)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 5)
    plt.plot(time_labels_3, Iout_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(760, 860)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 6)
    plt.plot(time_labels_2, Iout_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(760, 860)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    '''
    # Third subplot (Iin_Hi)
    plt.subplot(8, 3, i + 7)
    plt.plot(time_labels_1, Iin_hi_1, 'g-', label=test_key_1)
    plt.ylabel('I in Hi')
    #min_val = min(x for x in Iin_1 if x is not None)-2
    #max_val = max(x for x in Iin if x is not None)+2
    #plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(8, 3, i + 8)
    plt.plot(time_labels_3, Iin_hi_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    #plt.xticks([])
    
    plt.subplot(8, 3, i + 9)
    plt.plot(time_labels_2, Iin_hi_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    '''
    '''
    # Forth subplot (Iin_Hi)
    plt.subplot(8, 3, i + 10)
    plt.plot(time_labels_1, Iout_hi_1, 'g-', label=test_key_1)
    plt.ylabel('I out Hi')
    #min_val = min(x for x in Iin_1 if x is not None)-2
    #max_val = max(x for x in Iin if x is not None)+2
    #plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(8, 3, i + 11)
    plt.plot(time_labels_3, Iout_hi_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    #plt.xticks([])
    
    plt.subplot(8, 3, i + 12)
    plt.plot(time_labels_2, Iout_hi_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    '''
    '''
    # Fifth subplot (Iin_Hi)
    plt.subplot(8, 3, i + 13)
    plt.plot(time_labels_1, Iin_lo_1, 'g-', label=test_key_1)
    plt.ylabel('I in Lo')
    #min_val = min(x for x in Iin_1 if x is not None)-2
    #max_val = max(x for x in Iin if x is not None)+2
    #plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(8, 3, i + 14)
    plt.plot(time_labels_3, Iin_lo_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    #plt.xticks([])
    
    plt.subplot(8, 3, i + 15)
    plt.plot(time_labels_2, Iin_lo_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    '''
    '''
    # Sixth subplot (Iin_Hi)
    plt.subplot(8, 3, i + 16)
    plt.plot(time_labels_1, Iout_lo_1, 'g-', label=test_key_1)
    plt.ylabel('I out Lo')
    #min_val = min(x for x in Iin_1 if x is not None)-2
    #max_val = max(x for x in Iin if x is not None)+2
    #plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(8, 3, i + 17)
    plt.plot(time_labels_3, Iout_lo_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    #plt.xticks([])
    
    plt.subplot(8, 3, i + 18)
    plt.plot(time_labels_2, Iout_lo_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    '''
    
    # Seventh subplot (Vin)
    plt.subplot(4, 3, i + 7)
    plt.plot(time_labels_1, Vin_1, 'g-', label=test_key_1)
    plt.ylabel('V in (V)')
    min_val = min(x for x in Vin_2 if x is not None)-15
    max_val = max(x for x in Vin_2 if x is not None)+15
    plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    
    plt.subplot(4, 3, i + 8)
    plt.plot(time_labels_3, Vin_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 9)
    plt.plot(time_labels_2, Vin_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    
    # Eighth subplot (Vout)
    plt.subplot(4, 3, i + 10)
    plt.plot(time_labels_1, Vout_1, 'g-', label=test_key_1)
    plt.ylabel('V out (V)')
    min_val = min(x for x in Vout_1 if x is not None)-15
    max_val = max(x for x in Vout_1 if x is not None)+15
    plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 11)
    plt.plot(time_labels_3, Vout_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 12)
    plt.plot(time_labels_2, Vout_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95], h_pad=2)  # Adjust layout to add free space above the plot and leave space for the title
    plt.savefig(path + "/results/20240404/Plots/amac_el_plot_" + "20240404" + "_" + ".png", dpi=300)
    #plt.savefig(path + "\\results\\20240404\\Plots\\env_plot_" + "20240404" + "_" + ".png", dpi=500)
    plt.show()
    
    
    plt.figure(figsize=(25, 12))  # Adjust figure size as needed
    plt.suptitle('Plot of test interval AMAC module components temperature data (2024.04.04)', fontsize=25)
    
    plt.subplot(3, 3, i + 1)
    plt.plot(time_labels_1, NTCx_1, 'g-', label=test_key_1)
    plt.ylabel('NTCx (°C)')
    plt.title("LTRT COLD TEST 1")
    min_val = min(x for x in NTCx_2 if x is not None)-1
    max_val = max(x for x in NTCx_2 if x is not None)+1
    plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(3, 3, i + 2)
    plt.plot(time_labels_3, NTCx_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    plt.title("IDLE")
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(3, 3, i + 3)
    plt.plot(time_labels_2, NTCx_2, 'b-', label=test_key_2)
    plt.title("LTRT COLD TEST 2")
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    
    plt.subplot(3, 3, i + 4)
    plt.plot(time_labels_1, NTCy_1, 'g-', label=test_key_1)
    plt.ylabel('NTCy (°C)')
    min_val = min(x for x in NTCy_1 if x is not None)-1
    max_val = max(x for x in NTCy_1 if x is not None)+1
    plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(3, 3, i + 5)
    plt.plot(time_labels_3, NTCy_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(3, 3, i + 6)
    plt.plot(time_labels_2, NTCy_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    
    plt.subplot(3, 3, i + 7)
    plt.plot(time_labels_1, NTCpb_1, 'g-', label=test_key_1)
    plt.ylabel('NTCpb (°C)')
    min_val = min(x for x in NTCpb_1 if x is not None)-1
    max_val = max(x for x in NTCpb_1 if x is not None)+1
    plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(3, 3, i + 8)
    plt.plot(time_labels_3, NTCpb_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    plt.grid(True) 
    #plt.xticks([])
    
    plt.subplot(3, 3, i + 9)
    plt.plot(time_labels_2, NTCpb_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.grid(True) 
    #plt.xticks([])
    
    
    
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95], h_pad=2)  # Adjust layout to add free space above the plot and leave space for the title
    plt.savefig(path + "/results/20240404/Plots/amac_temp_plot_" + "20240404" + "_" + ".png", dpi=300)
    #plt.savefig(path + "\\results\\20240404\\Plots\\env_plot_" + "20240404" + "_" + ".png", dpi=500)
    plt.show()


    



'''
for key, test in all_results.items():

    time_labels = [datetime.fromisoformat(t).strftime('%H:%M:%S') for t in test["time"]]
    
    plt.figure(figsize=(16, 25))
    plt.suptitle('Plot of test interval environmental data of '+ key, fontsize=20)
    
    plt.subplot(4, 1, 1)
    plt.plot(time_labels, test["dp4"], 'r-')
    plt.ylabel('Dew Point')
    plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 
        
    plt.subplot(4, 1, 2)
    plt.plot(time_labels, test["rh4"], 'r-')
    plt.ylabel('Relative Humidity')
    plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 
    
    plt.subplot(4, 1, 3)
    plt.plot(time_labels, test["rh4_temp"], 'g-')
    plt.ylabel('Dew Point_temp (°C)')
    plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 
        
    plt.subplot(4, 1, 4)
    plt.plot(time_labels, test["temp_4"], 'g-')
    plt.ylabel('Temperature (°C)')
    plt.xlabel('Timestamps')
    plt.ylim(-35, 20)
    plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.98], h_pad=2)  # Adjust layout to prevent overlap
    plt.savefig(path+"\\results\\20240404\\Plots\\env_plot_" + key + ".png", dpi=500)
    plt.show()
'''

'''
# Plot each read-out with individual fit
###!!!Works only with detailed data NOT MEAN!!!###
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple']
for sublist1, sublist2, color in zip(xval, yval, colors):
    plt.scatter(sublist1, sublist2, marker="o")
    # Calculate linear fit for the current pair of sublists
    coeffs = np.polyfit(sublist1, sublist2, 1)
    fitted_line = np.polyval(coeffs, sublist1)
    
    # Plot the linear fit line
    #plt.plot(sublist1, fitted_line, color=color, linestyle='--')
plt.title('vt50_under vs. gain_under')
plt.xlabel('vt50_under')
plt.ylabel('gain_under')
plt.legend()
plt.show()
'''