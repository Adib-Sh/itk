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
file = "/results/20240404/output20240404/test_data_2024-04-04.json"
#file = "\\results\\20240404\\output20240404\\test_data_2024-04-04.json"
reader = get_data(file)
data = reader.test_env_data()


#Data for plots

#Chuck 4 data
all_results = {}
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
test1 = all_results["LTRT_COLD_TEST_1"]
test2 = all_results["LTRT_COLD_TEST_2"]

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
    dp4_1 = test_data_1["dp4"]
    rh4_1 = test_data_1["rh4"]
    rh4_temp_1 = test_data_1["rh4_temp"]
    temp_4_1 = test_data_1["temp_4"]
    
    time_labels_2 = [datetime.fromisoformat(t).strftime('%H:%M:%S') for t in test_data_2["time"]]
    dp4_2 = none_zero(test_data_2["dp4"])
    rh4_2 = none_zero(test_data_2["rh4"])
    rh4_temp_2 = none_zero(test_data_2["rh4_temp"])
    temp_4_2 = none_zero(test_data_2["temp_4"])

    time_labels_3 = [datetime.fromisoformat(t).strftime('%H:%M:%S') for t in test_data_3["time"]]
    dp4_3 = test_data_3["dp4"]
    rh4_3 = test_data_3["rh4"]
    rh4_temp_3 = test_data_3["rh4_temp"]
    temp_4_3 = test_data_3["temp_4"]
    
    
    # Filter out null values
    time_labels_3 = [t for t, v in zip(time_labels_3, temp_4_3) if v is not None]
    dp4_3 = [v for v in dp4_3 if v is not None]
    rh4_3 = [v for v in rh4_3 if v is not None]
    rh4_temp_3 = [v for v in rh4_temp_3 if v is not None]
    temp_4_3 = [v for v in temp_4_3 if v is not None]
    dp4_3 = dp4_3[:-1]  # Exclude last value
    rh4_3 = rh4_3[:-1]  # Exclude last value
    rh4_temp_3 = rh4_temp_3[:-1]  # Exclude last value
    temp_4_3 = temp_4_3[:-1]  # Exclude last value
    
    # Plotting
    plt.figure(figsize=(25, 12))  # Adjust figure size as needed
    plt.suptitle('Plot of test interval environmental data (2024.04.04)', fontsize=20)
    
    # First subplot (Temperature)
    plt.subplot(4, 3, i + 1)
    plt.plot(time_labels_1, temp_4_1, 'g-', label=test_key_1)
    plt.ylabel('Temperature (°C)')
    min_val = min(x for x in temp_4_1 if x is not None)-0.5
    max_val = max(x for x in temp_4_1 if x is not None)+0.5
    plt.ylim(min_val, max_val)
    plt.title("LTRT COLD TEST 1")
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 2)
    plt.plot(time_labels_3, temp_4_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.title("IDLE")
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1))
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 3)
    plt.plot(time_labels_2, temp_4_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks([])
    plt.title("LTRT COLD TEST 2")
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])

    # Second subplot (Dew Point)
    plt.subplot(4, 3, i + 4)
    plt.plot(time_labels_1, dp4_1, 'g-', label=test_key_1)
    plt.ylabel('Dew Point (°C)')
    min_val = min(x for x in dp4_1 if x is not None)-3
    max_val = max(x for x in dp4_1 if x is not None)+1
    plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 5)
    plt.plot(time_labels_3, dp4_3, 'r-', label=test_key_3)
    plt.ylim(min_val, max_val)
    #plt.yticks([])  # Remove y-axis labels
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 6)
    plt.plot(time_labels_2, dp4_2, 'b-', label=test_key_2)
    plt.ylim(min_val, max_val)
    #plt.yticks([])  # Remove y-axis labels
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    # Third subplot (Relative Humidity)
    plt.subplot(4, 3, i + 7)
    plt.plot(time_labels_1, rh4_1, 'g-', label=test_key_1)
    plt.ylabel('Relative Humidity')
    min_val = min(x for x in rh4_1 if x is not None)-0.08
    max_val = max(x for x in rh4_1 if x is not None)+0.08
    plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 8)
    plt.plot(time_labels_3, rh4_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1)) 
    #plt.xticks([])
    
    plt.subplot(4, 3, i + 9)
    plt.plot(time_labels_2, rh4_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    plt.ylim(min_val, max_val)
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    #plt.xticks([])
    
    # Fourth subplot (Dew Point Temperature)
    plt.subplot(4, 3, i + 10)
    plt.plot(time_labels_1, rh4_temp_1, 'g-', label=test_key_1)
    plt.ylabel('RH Temperature (°C)')
    plt.xlabel('Timestamps')
    min_val = 16#min(x for x in rh4_temp_1 if x is not None)-0.2
    max_val = 21#max(x for x in rh4_temp_1 if x is not None)+0.2
    plt.ylim(min_val, max_val)
    
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 

    plt.subplot(4, 3, i + 11)
    plt.plot(time_labels_3, rh4_temp_3, 'r-', label=test_key_3)
    #plt.yticks([])  # Remove y-axis labels
    plt.xticks(ticks=range(0, len(time_labels_3), len(time_labels_3) // 9 + 1)) 
    plt.ylim(min_val, max_val)
    
    
    plt.subplot(4, 3, i + 12)
    plt.plot(time_labels_2, rh4_temp_2, 'b-', label=test_key_2)
    #plt.yticks([])  # Remove y-axis labels
    plt.xticks(ticks=range(0, len(time_labels_1), len(time_labels_1) // 9 + 1)) 
    plt.ylim(min_val, max_val)

    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95], h_pad=2)  # Adjust layout to add free space above the plot and leave space for the title
    plt.savefig(path + "/results/20240404/Plots/env_plot_" + "20240404" + ".png", dpi=300)
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