import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

path = os.getcwd()
class get_data():
    def __init__(self):
        self.path = os.getcwd()
        self.rc_file = self.path + "\\results\\20240404\\test_data.json"

    
    def test_env_data(self):
        with open(self.rc_file, "r") as file:
            data = json.load(file)
            
        return data
    
    
#Read Data
reader = get_data()
test_env_data = reader.test_env_data()


#Data for plots

#Chuck 4 data
time =  test_env_data["timestamps"]
time_labels = [datetime.fromisoformat(t).strftime('%H:%M:%S') for t in time]
dp4 =  test_env_data["DP.4"]
rh4 =  test_env_data["RH.4"]
dp4_temp =  test_env_data["RH.4.temperature"]
temp_4 =  test_env_data["thermometer.C4"]




#Plots
'''
xval= vt50_under
yval= gain_under
channels_len = sum(len(results) for results in yval)
#channels_len = len(yval)
channels = np.linspace(0, channels_len, channels_len)
plt.scatter(channels, yval, marker='o', linestyle='-')
plt.title('vt50_under vs. gain_under')
plt.xlabel('vt50_under')
plt.ylabel('gain_under')
plt.legend()
plt.show()
'''

# Creating subplots
# Plotting the first set of data
plt.figure(figsize=(16, 10))
plt.suptitle('Plot of test interval environmental data ', fontsize=20)


plt.subplot(2, 2, 1)
plt.plot(time_labels, dp4, 'r-')
plt.ylabel('dew_point')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 
    
plt.subplot(2, 2, 2)
plt.plot(time_labels, rh4, 'r-')
plt.ylabel('relative_humidity')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 

plt.subplot(2, 2, 3)
plt.plot(time_labels, dp4_temp, 'g-')
plt.ylabel('dew_point_temp')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 
    
plt.subplot(2, 2, 4)
plt.plot(time_labels, temp_4, 'g-')
plt.ylabel('temperature')
plt.ylim(-35, 20)
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 

plt.tight_layout()  # Adjust layout to prevent overlap
plt.savefig(path+"\\results\\20240404\\Plots\\env_plot.png", dpi=500)
plt.show()


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