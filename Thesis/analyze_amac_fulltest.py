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
    
    # Add DP.1 and timestamps to the results dictionary
    all_results[test_key] = {
        "time": timestamps,
        "Iin": Iin,
        "Iout": Iout,
        "Iin_Hi": Iin_hi,
        "Iout_Hi": Iout_hi
        }
test1 = all_results["LTRT_COLD_TEST_1"]
test2 = all_results["LTRT_COLD_TEST_2"]
'''
#Read idle Data
file = "/results/20240404/output20240404/idle_data_2024-04-04.json"
#file = "\\results\\20240404\\output20240404\\idle_data_2024-04-04.json"
reader = get_data(file)
data = reader.test_env_data()

for test_key, test_data in data.items():
    # Extract DP.1 and timestamps from the test data
    timestamps = test_data.get("results", {}).get("timestamps", [])
    dp4 = test_data.get("results", {}).get("DP.4", [])
    rh4 = test_data.get("results", {}).get("RH.4", [])
    rh4_temp = test_data.get("results", {}).get("RH.4.temperature", [])
    temp_4 = test_data.get("results", {}).get("thermometer.C4", [])
    
    # Add DP.1 and timestamps to the results dictionary
    all_results[test_key] = {
        "time": timestamps,
        "dp4": dp4,
        "rh4": rh4,
        "rh4_temp": rh4_temp,
        "temp_4": temp_4
        }
'''
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
    Iout_hi_1 = test_data_1["Iout_Hi"]
    
    time_labels_3 = [datetime.fromisoformat(t).strftime('%H:%M:%S') for t in test_data_3["time"]]
    time_labels_3 = time_labels_3[:-1]
    Iin_3 = test_data_3["Iin"]
    #val_range_3 = int(len(Iin_3)/2)-1
    Iin_3 = Iin_3[:-1]
    Iout_3 = test_data_3["Iout"]
    Iout_3 = Iout_3[:-1]
    Iin_hi_3 = test_data_3["Iin_Hi"]
    Iout_hi_3 = test_data_3["Iout_Hi"]
    
    time_labels_2 = [datetime.fromisoformat(t).strftime('%H:%M:%S') for t in test_data_2["time"]]
    time_labels_2 = time_labels_2[:-1]
    Iin_2 = test_data_2["Iin"]
    val_range_2 = int(len(Iin_2)/2)+1
    Iin_2 = Iin_2[val_range_2:]
    Iout_2 = test_data_2["Iout"]
    Iout_2 = Iout_2[val_range_2:]
    Iin_hi_2 = test_data_2["Iin_Hi"]
    Iout_hi_2 = test_data_2["Iout_Hi"]

    
    '''
    # Filter out null values
    time_labels_3 = [t for t, v in zip(time_labels_3, Iin) if v is not None]
    time_range_3 = (len(time_labels_3)/2)
    time_label_3 = time_labels_3[:time_range_3]
    dp4_3 = [v for v in dp4_3 if v is not None]
    rh4_3 = [v for v in rh4_3 if v is not None]
    rh4_temp_3 = [v for v in rh4_temp_3 if v is not None]
    temp_4_3 = [v for v in temp_4_3 if v is not None]
    dp4_3 = dp4_3[:-1]  # Exclude last value
    rh4_3 = rh4_3[:-1]  # Exclude last value
    rh4_temp_3 = rh4_temp_3[:-1]  # Exclude last value
    temp_4_3 = temp_4_3[:-1]  # Exclude last value
    '''    
    # Plotting
    plt.figure(figsize=(25, 12))  # Adjust figure size as needed
    plt.suptitle('Plot of test interval environmental data (2024.04.04)', fontsize=20)
    
    # First subplot (Iin)
    plt.subplot(4, 3, i + 1)
    plt.plot(time_labels_1, Iin_1, 'g-', label=test_key_1)
    plt.ylabel('I_in')
    #min_val = min(x for x in Iin_1 if x is not None)-2
    #max_val = max(x for x in Iin if x is not None)+2
    #plt.ylim(min_val, max_val)
    plt.title("LTRT COLD TEST 1")
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 2)
    plt.plot(time_labels_3, Iin_3, 'r-', label=test_key_3)
    plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.title("IDLE")
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 3)
    plt.plot(time_labels_2, Iin_2, 'b-', label=test_key_2)
    plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.title("LTRT COLD TEST 2")
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])

    # Second subplot (Iout)
    plt.subplot(4, 3, i + 4)
    plt.plot(time_labels_1, Iout_1, 'g-', label=test_key_1)
    plt.ylabel('I_in')
    #min_val = min(x for x in Iin_1 if x is not None)-2
    #max_val = max(x for x in Iin if x is not None)+2
    #plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 5)
    plt.plot(time_labels_3, Iout_3, 'r-', label=test_key_3)
    plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 6)
    plt.plot(time_labels_2, Iout_2, 'b-', label=test_key_2)
    plt.yticks([])  # Remove y-axis labels
    #plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    



    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95], h_pad=2)  # Adjust layout to add free space above the plot and leave space for the title
    plt.savefig(path + "/results/20240404/Plots/amac_plot_" + "20240404" + "_" + ".png", dpi=500)
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